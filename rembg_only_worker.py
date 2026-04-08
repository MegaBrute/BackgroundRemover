"""
rembg-only worker - runs in separate process to avoid DLL conflicts with PyQt5.
Uses GPU (CUDA) when available.
"""
import sys
import os
import json

# Clean up sys.path
sys.path = [p for p in sys.path if 'scoop' not in p.lower() and 'mpv' not in p.lower()]

# Add cuDNN/CUDA DLL directories for GPU support
venv_dir = os.path.dirname(os.path.dirname(sys.executable))
cuda_paths = [
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cudnn", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cublas", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "nvidia", "cuda_runtime", "bin"),
    os.path.join(venv_dir, "Lib", "site-packages", "torch", "lib"),
]
for cuda_path in cuda_paths:
    if os.path.isdir(cuda_path):
        try:
            os.add_dll_directory(cuda_path)
        except (AttributeError, OSError):
            pass
        os.environ["PATH"] = cuda_path + os.pathsep + os.environ.get("PATH", "")

from PIL import Image
from rembg import remove, new_session

# Cache session
session = None
current_model = None


def get_session(model_name):
    global session, current_model
    if current_model != model_name:
        session = new_session(model_name)
        current_model = model_name
    return session


def process_frame(input_path, output_path, model="u2net"):
    """Process a single frame."""
    img = Image.open(input_path)
    sess = get_session(model)
    result = remove(img, session=sess)
    result.save(output_path, format="PNG")


def main():
    print("READY", flush=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == "QUIT":
            break

        try:
            cmd = json.loads(line)
            process_frame(
                cmd["input"],
                cmd["output"],
                cmd.get("model", "u2net")
            )
            print("OK", flush=True)
        except Exception as e:
            print(f"ERROR:{e}", flush=True)


if __name__ == "__main__":
    main()
