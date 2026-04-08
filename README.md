# GIF Background Remover

A desktop GUI application for removing backgrounds from GIFs with multiple AI engines and manual editing tools.

## Features

### Background Removal Engines
- **Color Key** - Fast, instant removal for solid color backgrounds (like green screen)
- **RVM (Robust Video Matting)** - AI with temporal memory for consistent results across frames
- **rembg** - General-purpose AI background removal
- **SAM 2** - Click-to-segment with video propagation
- **Auto + SAM 2** - Automatic detection + temporal propagation

### Editing Tools
- **Frame scrubber** - Navigate through frames with thumbnail strip
- **Multi-select frames** - Shift+click, Ctrl+click, or drag to select multiple frames
- **Delete frames** - Remove unwanted frames individually or in bulk
- **Trim** - Set start/end points, delete outside trim range
- **Mask painting** - Paint/erase to fix mask errors manually

### Export Options
- **Formats**: GIF, WebP, APNG, WebM (video)
- **Compression**: Auto-compress to target size (e.g., 256KB for Telegram)
- **Resize**: Scale presets, 512x512 fit (for Telegram stickers), custom dimensions
- **Captions**: Add text overlays with customizable font, size, position

### Other Features
- Drag & drop GIF loading
- Replace background with color or image
- Preview with checkerboard or custom background
- Frame duration editing
- Playback speed control

## Installation

### Requirements
- Python 3.8+
- Windows (tested), should work on macOS/Linux with minor adjustments

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gif-background-remover.git
cd gif-background-remover
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
python gif_background_remover.py
```

### Optional: WebM Export
For WebM export, install [FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.

### Optional: SAM 2
SAM 2 model (~900MB) will auto-download on first use, or you can manually download `sam2.1_hiera_large.pt` to the project directory.

## Usage

1. **Load a GIF** - Drag & drop or click "Open GIF"
2. **Choose an engine** - Color Key for solid backgrounds, RVM/rembg for complex scenes
3. **Remove background** - Click "Remove Background"
4. **Edit if needed** - Use mask painting tools to fix errors
5. **Export** - Choose format and save

### Keyboard Shortcuts
- **Space** - Play/pause
- **Left/Right arrows** - Previous/next frame
- **Delete** - Delete current frame

### Frame Selection
- **Click** - Select single frame
- **Shift+Click** - Select range
- **Ctrl+Click** - Toggle frame in selection
- **Drag** - Select range by dragging
- **Right-click** - Deselect frame

## Dependencies

See `requirements.txt`. Main dependencies:
- PyQt5 - GUI framework
- Pillow - Image processing
- rembg - Background removal AI
- torch - For RVM and SAM 2
- numpy - Array operations

## License

MIT License - see LICENSE file

## Contributing

Pull requests welcome! Please open an issue first to discuss major changes.
