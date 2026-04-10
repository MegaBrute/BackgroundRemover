"""
SAM 2 Video Segmentation Worker
Processes video frames with click-based prompting and temporal propagation.
"""

import sys
import os
import json
import tempfile
import shutil

# Add CUDA DLL paths
venv_dir = os.path.dirname(os.path.dirname(sys.executable))
cuda_paths = [
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cudnn", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cublas", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cuda_runtime", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "torch", "lib"),
]
for cuda_path in cuda_paths:
    if os.path.isdir(cuda_path):
        os.add_dll_directory(cuda_path)
        os.environ["PATH"] = cuda_path + os.pathsep + os.environ.get("PATH", "")

import torch
import numpy as np
from PIL import Image


def find_sam2_checkpoint():
    """Find SAM 2 checkpoint file."""
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # SAM 2 checkpoint names (in order of preference - larger = better)
    checkpoints = [
        ("sam2.1_hiera_large.pt", "configs/sam2.1/sam2.1_hiera_l.yaml"),
        ("sam2.1_hiera_base_plus.pt", "configs/sam2.1/sam2.1_hiera_b+.yaml"),
        ("sam2.1_hiera_small.pt", "configs/sam2.1/sam2.1_hiera_s.yaml"),
        ("sam2.1_hiera_tiny.pt", "configs/sam2.1/sam2.1_hiera_t.yaml"),
        ("sam2_hiera_large.pt", "configs/sam2/sam2_hiera_l.yaml"),
        ("sam2_hiera_base_plus.pt", "configs/sam2/sam2_hiera_b+.yaml"),
        ("sam2_hiera_small.pt", "configs/sam2/sam2_hiera_s.yaml"),
        ("sam2_hiera_tiny.pt", "configs/sam2/sam2_hiera_t.yaml"),
    ]

    for ckpt_name, config in checkpoints:
        ckpt_path = os.path.join(app_dir, ckpt_name)
        if os.path.exists(ckpt_path):
            return ckpt_path, config

    # Check in checkpoints subdirectory
    ckpt_dir = os.path.join(app_dir, "checkpoints")
    if os.path.isdir(ckpt_dir):
        for ckpt_name, config in checkpoints:
            ckpt_path = os.path.join(ckpt_dir, ckpt_name)
            if os.path.exists(ckpt_path):
                return ckpt_path, config

    return None, None


def load_predictor(checkpoint_path, config_name):
    """Load SAM 2 video predictor."""
    from sam2.build_sam import build_sam2_video_predictor

    device = "cuda" if torch.cuda.is_available() else "cpu"

    predictor = build_sam2_video_predictor(
        config_name,
        checkpoint_path,
        device=device
    )

    return predictor, device


def process_video(frame_dir, click_points=None, click_labels=None, click_frame_idx=0, mask_path=None):
    """
    Process video frames with SAM 2.

    Args:
        frame_dir: Directory containing frames as 00000.jpg, 00001.jpg, etc.
        click_points: List of [x, y] coordinates (optional if mask_path provided)
        click_labels: List of labels (1=foreground, 0=background)
        click_frame_idx: Frame index where clicks/mask were made
        mask_path: Path to initial mask image (optional, alternative to clicks)

    Returns:
        Dict mapping frame index to mask array
    """
    checkpoint_path, config_name = find_sam2_checkpoint()

    if checkpoint_path is None:
        raise RuntimeError(
            "SAM 2 checkpoint not found. Please download from:\n"
            "https://github.com/facebookresearch/sam2#download-checkpoints\n"
            "Place the .pt file in the app folder."
        )

    predictor, device = load_predictor(checkpoint_path, config_name)

    # Initialize video state (offload to CPU to avoid GPU OOM)
    inference_state = predictor.init_state(
        video_path=frame_dir,
        offload_video_to_cpu=True,
        async_loading_frames=True
    )

    # Reset state
    predictor.reset_state(inference_state)

    if mask_path and os.path.exists(mask_path):
        # Use bounding box from mask - more robust than single point
        mask_img = Image.open(mask_path).convert("L")
        mask_array = np.array(mask_img) > 128  # Binary mask

        y_coords, x_coords = np.where(mask_array)
        if len(x_coords) > 0:
            # Get bounding box with padding
            min_x, max_x = int(np.min(x_coords)), int(np.max(x_coords))
            min_y, max_y = int(np.min(y_coords)), int(np.max(y_coords))

            width = max_x - min_x
            height = max_y - min_y
            pad_x = int(width * 0.05)
            pad_y = int(height * 0.05)

            box = np.array([
                max(0, min_x - pad_x),
                max(0, min_y - pad_y),
                min(mask_array.shape[1], max_x + pad_x),
                min(mask_array.shape[0], max_y + pad_y)
            ], dtype=np.float32)

            _, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
                inference_state=inference_state,
                frame_idx=click_frame_idx,
                obj_id=1,
                box=box,
            )
        else:
            raise RuntimeError("Mask is empty - rembg failed to detect subject")
    elif click_points:
        # Use point prompts
        points = np.array(click_points, dtype=np.float32)
        labels = np.array(click_labels, dtype=np.int32)

        _, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=click_frame_idx,
            obj_id=1,
            points=points,
            labels=labels,
        )
    else:
        raise RuntimeError("Either click_points or mask_path must be provided")

    # Propagate through video
    masks = {}

    for frame_idx, obj_ids, mask_logits in predictor.propagate_in_video(inference_state):
        # mask_logits shape: (num_objects, 1, H, W)
        mask = (mask_logits[0] > 0.0).cpu().numpy().squeeze()
        masks[frame_idx] = mask

    return masks


def main():
    """Main worker loop - receives commands via stdin, outputs via stdout."""

    # Load predictor ONCE at startup
    checkpoint_path, config_name = find_sam2_checkpoint()
    if checkpoint_path is None:
        print(json.dumps({"status": "ERROR", "message": "SAM 2 checkpoint not found"}), flush=True)
        return

    try:
        predictor, device = load_predictor(checkpoint_path, config_name)
    except Exception as e:
        print(json.dumps({"status": "ERROR", "message": f"Failed to load SAM 2: {e}"}), flush=True)
        return

    print("READY", flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line or line == "QUIT":
            break

        try:
            cmd = json.loads(line)

            if cmd.get("action") == "process":
                frame_dir = cmd["frame_dir"]
                click_points = cmd.get("click_points")
                click_labels = cmd.get("click_labels")
                click_frame_idx = cmd.get("click_frame_idx", 0)
                mask_path = cmd.get("mask_path")  # Optional: initial mask from rembg
                output_dir = cmd["output_dir"]

                # Init state for this video (offload to CPU to avoid GPU OOM)
                inference_state = predictor.init_state(
                    video_path=frame_dir,
                    offload_video_to_cpu=True,
                    async_loading_frames=True
                )
                predictor.reset_state(inference_state)

                # Set up prompts
                if mask_path and os.path.exists(mask_path):
                    mask_img = Image.open(mask_path).convert("L")
                    mask_array = np.array(mask_img) > 128
                    y_coords, x_coords = np.where(mask_array)
                    if len(x_coords) > 0:
                        # Use bounding box instead of single point - more robust
                        min_x, max_x = int(np.min(x_coords)), int(np.max(x_coords))
                        min_y, max_y = int(np.min(y_coords)), int(np.max(y_coords))

                        # Add some padding (5%)
                        width = max_x - min_x
                        height = max_y - min_y
                        pad_x = int(width * 0.05)
                        pad_y = int(height * 0.05)

                        box = np.array([
                            max(0, min_x - pad_x),
                            max(0, min_y - pad_y),
                            min(mask_array.shape[1], max_x + pad_x),
                            min(mask_array.shape[0], max_y + pad_y)
                        ], dtype=np.float32)

                        predictor.add_new_points_or_box(
                            inference_state=inference_state,
                            frame_idx=click_frame_idx,
                            obj_id=1,
                            box=box,
                        )
                    else:
                        raise RuntimeError("Mask is empty")
                elif click_points:
                    points = np.array(click_points, dtype=np.float32)
                    labels = np.array(click_labels, dtype=np.int32)
                    predictor.add_new_points_or_box(
                        inference_state=inference_state,
                        frame_idx=click_frame_idx,
                        obj_id=1,
                        points=points,
                        labels=labels,
                    )
                else:
                    raise RuntimeError("No prompts provided")

                # Propagate with progress
                num_frames = 0
                for frame_idx, obj_ids, mask_logits in predictor.propagate_in_video(inference_state):
                    mask = (mask_logits[0] > 0.0).cpu().numpy().squeeze()

                    # Load original frame
                    frame_path = os.path.join(frame_dir, f"{frame_idx:05d}.jpg")
                    if not os.path.exists(frame_path):
                        frame_path = os.path.join(frame_dir, f"{frame_idx:05d}.png")

                    img = Image.open(frame_path).convert("RGBA")
                    alpha = (mask * 255).astype(np.uint8)
                    alpha_img = Image.fromarray(alpha).resize(img.size, Image.Resampling.LANCZOS)
                    img.putalpha(alpha_img)

                    out_path = os.path.join(output_dir, f"{frame_idx:05d}.png")
                    img.save(out_path)
                    num_frames += 1

                    # Report progress per frame
                    print(json.dumps({"status": "PROGRESS", "frame": frame_idx, "total": num_frames}), flush=True)

                    # Clear GPU memory periodically
                    del mask_logits
                    if num_frames % 10 == 0:
                        torch.cuda.empty_cache()

                print(json.dumps({"status": "OK", "num_frames": num_frames}), flush=True)

            elif cmd.get("action") == "check":
                # Check if SAM 2 is ready
                checkpoint_path, config_name = find_sam2_checkpoint()
                if checkpoint_path:
                    print(json.dumps({
                        "status": "OK",
                        "checkpoint": os.path.basename(checkpoint_path),
                        "device": "cuda" if torch.cuda.is_available() else "cpu"
                    }), flush=True)
                else:
                    print(json.dumps({
                        "status": "NO_CHECKPOINT",
                        "message": "SAM 2 checkpoint not found"
                    }), flush=True)

            else:
                print(json.dumps({"status": "ERROR", "message": "Unknown action"}), flush=True)

        except Exception as e:
            import traceback
            print(json.dumps({
                "status": "ERROR",
                "message": str(e),
                "traceback": traceback.format_exc()
            }), flush=True)


if __name__ == "__main__":
    main()
