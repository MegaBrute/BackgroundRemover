"""
RVM-only worker - completely separate from rembg to avoid any onnxruntime issues.
"""
import sys
import os
import json

# Clean up sys.path
sys.path = [p for p in sys.path if 'scoop' not in p.lower() and 'mpv' not in p.lower()]

import torch
import numpy as np
from PIL import Image

# Disable gradients
torch.set_grad_enabled(False)

# Global state
model = None
device = None
rec = [None] * 4  # Temporal memory
last_size = None


def load_model():
    global model, device

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading RVM on {device}...", file=sys.stderr)

    model = torch.hub.load(
        "PeterL1n/RobustVideoMatting",
        "mobilenetv3",
        trust_repo=True
    ).to(device).eval()

    print("RVM ready.", file=sys.stderr)


def process_frame(img_path, out_path, downsample_ratio=None, warmup=False):
    """Process a single frame with temporal memory."""
    global rec, last_size

    img = Image.open(img_path).convert("RGB")
    w, h = img.size

    # Reset temporal memory if size changed
    if last_size != (w, h):
        rec = [None] * 4
        last_size = (w, h)

        # Warmup: process this frame multiple times to initialize temporal memory
        # This prevents the "fade in" effect on the first frames
        if not warmup:
            print("WARMUP:Initializing temporal memory...", file=sys.stderr)
            for _ in range(5):
                process_frame(img_path, out_path, downsample_ratio, warmup=True)
            print("WARMUP:Done", file=sys.stderr)

    # Auto downsample ratio
    if downsample_ratio is None:
        downsample_ratio = min(512 / max(h, w), 1.0)

    # Convert to tensor
    src = torch.from_numpy(np.array(img)).float() / 255.0
    src = src.permute(2, 0, 1).unsqueeze(0).to(device)

    # Process with temporal memory
    with torch.no_grad():
        fgr, pha, *new_rec = model(src, *rec, downsample_ratio)

    # Update temporal memory
    rec = new_rec

    # Don't save during warmup
    if warmup:
        return

    # Convert to RGBA
    fgr = fgr.squeeze(0).cpu().numpy().transpose(1, 2, 0)
    pha = pha.squeeze(0).cpu().numpy().transpose(1, 2, 0)

    rgba = np.concatenate([fgr, pha], axis=2)
    rgba = (rgba * 255).clip(0, 255).astype(np.uint8)

    result = Image.fromarray(rgba, mode="RGBA")
    result.save(out_path, format="PNG")


def main():
    load_model()
    print("READY", flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == "QUIT":
            break

        try:
            cmd = json.loads(line)
            process_frame(cmd["input"], cmd["output"])
            print("OK", flush=True)
        except Exception as e:
            print(f"ERROR:{e}", flush=True)


if __name__ == "__main__":
    main()
