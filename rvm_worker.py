"""
RobustVideoMatting Worker
Processes GIF frames as a video sequence with temporal consistency.
Uses a recurrent neural network that maintains memory across frames.
"""

import sys
import os
import json
import torch
import numpy as np
from PIL import Image

# Disable gradients for inference
torch.set_grad_enabled(False)


class RVMProcessor:
    def __init__(self, variant="mobilenetv3", device=None):
        """
        Initialize RVM model.
        variant: "mobilenetv3" (faster) or "resnet50" (more accurate)
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"Loading RVM model ({variant}) on {self.device}...", file=sys.stderr)

        # Load model from torch hub
        self.model = torch.hub.load(
            "PeterL1n/RobustVideoMatting",
            variant,
            trust_repo=True
        ).to(self.device).eval()

        print("RVM model loaded.", file=sys.stderr)

    def process_frames(self, frames, downsample_ratio=None):
        """
        Process a list of PIL Image frames with temporal consistency.
        Returns list of RGBA PIL Images with background removed.

        The key difference from per-frame processing:
        - Recurrent state (rec) carries temporal information between frames
        - The model "remembers" what the subject looks like from previous frames
        """
        results = []

        # Initialize recurrent state (this is the temporal memory)
        rec = [None] * 4  # RVM uses 4 recurrent states

        # Auto-determine downsample ratio based on resolution
        if downsample_ratio is None:
            h, w = frames[0].height, frames[0].width
            if max(h, w) > 1080:
                downsample_ratio = 0.25
            elif max(h, w) > 720:
                downsample_ratio = 0.375
            else:
                downsample_ratio = 0.5

        for i, frame in enumerate(frames):
            # Convert PIL to tensor
            img = frame.convert("RGB")
            img_tensor = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
            img_tensor = img_tensor.unsqueeze(0).to(self.device)  # Add batch dim

            # Process with temporal memory
            # rec carries information from previous frames
            fgr, pha, *rec = self.model(img_tensor, *rec, downsample_ratio)

            # fgr = foreground RGB, pha = alpha matte
            # Combine into RGBA
            fgr = fgr.squeeze(0).cpu().numpy().transpose(1, 2, 0)
            pha = pha.squeeze(0).cpu().numpy().transpose(1, 2, 0)

            # Create RGBA output
            rgba = np.concatenate([fgr, pha], axis=2)
            rgba = (rgba * 255).clip(0, 255).astype(np.uint8)

            result = Image.fromarray(rgba, mode="RGBA")
            results.append(result)

            # Progress update
            print(f"PROGRESS:{i+1}/{len(frames)}", flush=True)

        return results


def main():
    """
    Worker process that receives commands via stdin.

    Protocol:
    1. Send "READY" when model is loaded
    2. Receive JSON command with input_dir, output_dir, frame_count
    3. Process all frames with temporal consistency
    4. Send "DONE" when complete
    """

    # Check for CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        processor = RVMProcessor(variant="mobilenetv3", device=device)
    except Exception as e:
        print(f"ERROR:Failed to load model: {e}", flush=True)
        sys.exit(1)

    print("READY", flush=True)

    for line in sys.stdin:
        line = line.strip()

        if line == "QUIT":
            break

        if not line.startswith("{"):
            continue

        try:
            cmd = json.loads(line)
            input_dir = cmd["input_dir"]
            output_dir = cmd["output_dir"]
            frame_count = cmd["frame_count"]
            downsample = cmd.get("downsample_ratio", None)

            # Load all frames
            frames = []
            for i in range(frame_count):
                img_path = os.path.join(input_dir, f"frame_{i:04d}.png")
                if os.path.exists(img_path):
                    frames.append(Image.open(img_path))
                else:
                    print(f"ERROR:Missing frame {img_path}", flush=True)
                    break

            if len(frames) != frame_count:
                print("ERROR:Frame count mismatch", flush=True)
                continue

            # Process with temporal consistency
            results = processor.process_frames(frames, downsample)

            # Save results
            for i, result in enumerate(results):
                out_path = os.path.join(output_dir, f"frame_{i:04d}.png")
                result.save(out_path, format="PNG")

            print("DONE", flush=True)

        except Exception as e:
            print(f"ERROR:{e}", flush=True)


if __name__ == "__main__":
    main()
