"""
GIF Background Remover Pro
A professional GUI application for removing and replacing backgrounds in GIFs.
"""

import sys
import os

# Clean up sys.path to remove scoop/mpv pollution
sys.path = [p for p in sys.path if 'scoop' not in p.lower() and 'mpv' not in p.lower()]

if getattr(sys, "frozen", False):
    app_dir = os.path.dirname(sys.executable)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    meipass_dir = getattr(sys, "_MEIPASS", None)
    dll_dirs = [app_dir, os.path.join(app_dir, "onnxruntime", "capi")]
    if meipass_dir:
        dll_dirs.append(meipass_dir)
        dll_dirs.append(os.path.join(meipass_dir, "onnxruntime", "capi"))
    for dll_dir in dll_dirs:
        if dll_dir and os.path.isdir(dll_dir):
            try:
                os.add_dll_directory(dll_dir)
            except (AttributeError, FileNotFoundError, OSError):
                pass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QMessageBox, QComboBox,
    QScrollArea, QFrame, QProgressBar, QSpinBox, QColorDialog, QGroupBox,
    QCheckBox, QTabWidget, QSplitter, QSizePolicy, QMenu, QAction, QToolButton,
    QLineEdit, QFontComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMimeData, QSize, QEvent
from PyQt5.QtGui import (
    QPixmap, QImage, QPainter, QColor, QIcon, QDragEnterEvent, QDropEvent,
    QPalette, QFont, QKeySequence, QFontDatabase
)
from PIL import Image, ImageSequence, ImageDraw, ImageFilter, ImageFont
import numpy as np
import io
import subprocess
import tempfile
import zipfile
import json
import shutil
import urllib.request
import traceback


# ============================================================================
# STYLES
# ============================================================================

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QGroupBox {
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: #9d9dff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}

QPushButton {
    background-color: #3a3a5a;
    color: #eaeaea;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #4a4a7a;
}

QPushButton:pressed {
    background-color: #2a2a4a;
}

QPushButton:disabled {
    background-color: #2a2a3a;
    color: #6a6a8a;
}

QPushButton#primaryBtn {
    background-color: #6c5ce7;
}

QPushButton#primaryBtn:hover {
    background-color: #7d6ef8;
}

QPushButton#dangerBtn {
    background-color: #e74c3c;
}

QPushButton#dangerBtn:hover {
    background-color: #f85c4c;
}

QPushButton#successBtn {
    background-color: #27ae60;
}

QPushButton#successBtn:hover {
    background-color: #37be70;
}

QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #3a3a5a;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #6c5ce7;
    border: none;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #7d6ef8;
}

QComboBox {
    background-color: #3a3a5a;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9d9dff;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #2a2a4a;
    border: 1px solid #3a3a5a;
    selection-background-color: #6c5ce7;
    border-radius: 6px;
}

QSpinBox {
    background-color: #3a3a5a;
    border: none;
    border-radius: 6px;
    padding: 8px;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #4a4a7a;
    border: none;
    width: 20px;
}

QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #3a3a5a;
    text-align: center;
    color: white;
    height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe);
    border-radius: 6px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:horizontal {
    border: none;
    background: #2a2a4a;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #4a4a7a;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    padding: 10px;
}

QTabBar::tab {
    background-color: #2a2a4a;
    color: #9a9aba;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #3a3a5a;
    color: #eaeaea;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    background-color: #3a3a5a;
}

QCheckBox::indicator:checked {
    background-color: #6c5ce7;
}

QLabel#dropZone {
    border: 3px dashed #4a4a7a;
    border-radius: 16px;
    background-color: #1e1e3a;
    color: #7a7a9a;
    font-size: 16px;
}

QLabel#dropZone:hover {
    border-color: #6c5ce7;
    background-color: #252550;
}
"""

def is_frozen_app():
    return bool(getattr(sys, "frozen", False))


def get_app_dir():
    if is_frozen_app():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# UTILITIES
# ============================================================================

def pil_to_qpixmap(pil_image):
    """Convert PIL Image to QPixmap."""
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    data = pil_image.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


def create_checkerboard(width, height, square_size=10, color1="#404040", color2="#303030"):
    """Create a checkerboard pattern for transparency preview."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            color = color1 if ((x // square_size) + (y // square_size)) % 2 == 0 else color2
            draw.rectangle([x, y, x + square_size, y + square_size], fill=color)
    return img


def create_solid_background(width, height, color):
    """Create a solid color background."""
    return Image.new("RGB", (width, height), color)


# ============================================================================
# BACKGROUND REMOVAL THREAD
# ============================================================================

class BackgroundRemovalThread(QThread):
    """Thread for background removal processing via subprocess."""
    progress = pyqtSignal(int, int, str)  # current, total, status message
    frame_done = pyqtSignal(int, object)  # index, result image
    finished_all = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, frames, deleted_frames, worker_command, model=None):
        super().__init__()
        self.frames = frames
        self.deleted_frames = deleted_frames
        self.worker_command = worker_command
        self.model = model

    def run(self):
        import time
        total = len(self.frames)
        temp_dir = tempfile.mkdtemp(prefix='rembg_')

        try:
            proc = subprocess.Popen(
                self.worker_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            ready = proc.stdout.readline().strip()
            if ready != "READY":
                self.error_occurred.emit(f"Worker failed to start: {ready}")
                return

        except Exception as e:
            self.error_occurred.emit(f"Failed to start worker: {str(e)}")
            return

        start_time = time.time()
        processed_count = 0

        fatal_error = None

        for i, frame in enumerate(self.frames):
            if i in self.deleted_frames:
                self.frame_done.emit(i, None)
                self.progress.emit(i + 1, total, f"Skipping deleted frame {i + 1}")
                continue

            try:
                input_path = os.path.join(temp_dir, f'input_{i}.png')
                output_path = os.path.join(temp_dir, f'output_{i}.png')
                frame.save(input_path, format='PNG')

                # Send JSON command to worker
                cmd_data = {
                    "input": input_path,
                    "output": output_path
                }
                if self.model:
                    cmd_data["model"] = self.model
                cmd = json.dumps(cmd_data)
                proc.stdin.write(cmd + '\n')
                proc.stdin.flush()

                result_line = proc.stdout.readline().strip()

                if result_line.startswith("ERROR:"):
                    raise RuntimeError(result_line[6:].strip())

                if result_line == 'OK' and os.path.exists(output_path):
                    result_img = Image.open(output_path).copy()
                    self.frame_done.emit(i, result_img)
                    os.remove(output_path)
                    processed_count += 1
                else:
                    raise RuntimeError(f"Unexpected worker response: {result_line or 'EMPTY'}")

                if os.path.exists(input_path):
                    os.remove(input_path)

                # Calculate ETA
                elapsed = time.time() - start_time
                if processed_count > 0:
                    avg_time = elapsed / processed_count
                    remaining = (total - i - 1) * avg_time
                    eta_str = f"ETA: {int(remaining)}s"
                else:
                    eta_str = "Calculating..."

                self.progress.emit(i + 1, total, f"Processing frame {i + 1}/{total} - {eta_str}")

            except Exception as e:
                fatal_error = f"Frame {i + 1} failed: {str(e)}"
                break

        try:
            proc.stdin.write('QUIT\n')
            proc.stdin.flush()
            proc.terminate()
        except:
            pass

        shutil.rmtree(temp_dir, ignore_errors=True)

        if fatal_error:
            self.error_occurred.emit(fatal_error)
        else:
            self.finished_all.emit()


class SAM2Thread(QThread):
    """Thread for SAM 2 video segmentation processing."""
    progress = pyqtSignal(str)  # status message
    frame_done = pyqtSignal(int, object)  # index, result image
    finished_all = pyqtSignal(int)  # num_frames processed
    error_occurred = pyqtSignal(str)

    def __init__(self, frames, deleted_frames, click_points, click_labels, click_frame_idx):
        super().__init__()
        self.frames = frames
        self.deleted_frames = deleted_frames
        self.click_points = click_points
        self.click_labels = click_labels
        self.click_frame_idx = click_frame_idx

    def run(self):
        temp_dir = tempfile.mkdtemp(prefix='sam2_')
        frame_dir = os.path.join(temp_dir, "frames")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(frame_dir)
        os.makedirs(output_dir)

        try:
            # Save frames as numbered images
            self.progress.emit("Saving frames...")
            for i, frame in enumerate(self.frames):
                if i not in self.deleted_frames:
                    frame_path = os.path.join(frame_dir, f"{i:05d}.jpg")
                    frame.convert("RGB").save(frame_path, "JPEG", quality=95)

            # Start SAM 2 worker
            self.progress.emit("Loading SAM 2 model (this takes a moment)...")

            worker_script = os.path.join(get_app_dir(), "sam2_worker.py")
            proc = subprocess.Popen(
                [sys.executable, worker_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait for ready
            ready = proc.stdout.readline().strip()
            if ready != "READY":
                stderr = proc.stderr.read()
                raise RuntimeError(f"SAM 2 worker failed to start: {ready}\n{stderr}")

            # Send process command
            cmd = {
                "action": "process",
                "frame_dir": frame_dir,
                "click_points": self.click_points,
                "click_labels": self.click_labels,
                "click_frame_idx": self.click_frame_idx,
                "output_dir": output_dir
            }

            self.progress.emit("Running SAM 2 segmentation...")

            proc.stdin.write(json.dumps(cmd) + "\n")
            proc.stdin.flush()

            # Read response
            response_line = proc.stdout.readline().strip()

            # Clean up process
            try:
                proc.stdin.write("QUIT\n")
                proc.stdin.flush()
                proc.terminate()
            except:
                pass

            if not response_line:
                stderr = proc.stderr.read()
                raise RuntimeError(f"No response from SAM 2 worker.\nStderr: {stderr}")

            response = json.loads(response_line)

            if response.get("status") != "OK":
                raise RuntimeError(response.get("message", "Unknown error") +
                                 "\n" + response.get("traceback", ""))

            # Load results
            self.progress.emit("Loading segmented frames...")
            num_loaded = 0

            for i in range(len(self.frames)):
                out_path = os.path.join(output_dir, f"{i:05d}.png")
                if os.path.exists(out_path):
                    result_img = Image.open(out_path).copy()
                    self.frame_done.emit(i, result_img)
                    num_loaded += 1

            self.finished_all.emit(num_loaded)

        except Exception as e:
            import traceback
            self.error_occurred.emit(f"{str(e)}\n\n{traceback.format_exc()}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class AutoSAM2Thread(QThread):
    """Thread for Auto + SAM 2 hybrid processing: rembg detects, SAM 2 propagates."""
    progress = pyqtSignal(str)  # status message
    frame_done = pyqtSignal(int, object)  # index, result image
    finished_all = pyqtSignal(int)  # num_frames processed
    error_occurred = pyqtSignal(str)

    def __init__(self, frames, deleted_frames):
        super().__init__()
        self.frames = frames
        self.deleted_frames = deleted_frames

    def run(self):
        temp_dir = tempfile.mkdtemp(prefix='auto_sam2_')
        frame_dir = os.path.join(temp_dir, "frames")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(frame_dir)
        os.makedirs(output_dir)

        try:
            # Step 1: Save frames
            self.progress.emit("Saving frames...")
            for i, frame in enumerate(self.frames):
                if i not in self.deleted_frames:
                    frame_path = os.path.join(frame_dir, f"{i:05d}.jpg")
                    frame.convert("RGB").save(frame_path, "JPEG", quality=95)

            # Step 2: Run rembg on first non-deleted frame to get initial mask
            first_frame_idx = 0
            for i in range(len(self.frames)):
                if i not in self.deleted_frames:
                    first_frame_idx = i
                    break

            self.progress.emit("Running rembg to detect subject...")

            # Start rembg worker to process first frame
            rembg_script = os.path.join(get_app_dir(), "rembg_only_worker.py")
            rembg_proc = subprocess.Popen(
                [sys.executable, rembg_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            ready = rembg_proc.stdout.readline().strip()
            if ready != "READY":
                raise RuntimeError(f"rembg worker failed: {ready}")

            # Process first frame with rembg
            input_path = os.path.join(frame_dir, f"{first_frame_idx:05d}.jpg")
            rembg_output = os.path.join(temp_dir, "rembg_result.png")
            mask_path = os.path.join(temp_dir, "initial_mask.png")

            cmd = json.dumps({"input": input_path, "output": rembg_output})
            rembg_proc.stdin.write(cmd + "\n")
            rembg_proc.stdin.flush()

            result = rembg_proc.stdout.readline().strip()
            rembg_proc.stdin.write("QUIT\n")
            rembg_proc.stdin.flush()
            rembg_proc.terminate()

            if result != "OK":
                raise RuntimeError(f"rembg failed: {result}")

            # Extract mask from rembg result
            rembg_img = Image.open(rembg_output).convert("RGBA")
            mask = rembg_img.split()[3]  # Get alpha channel
            mask.save(mask_path)

            self.progress.emit("Loading SAM 2 model...")

            # Step 3: Run SAM 2 with the mask
            sam2_script = os.path.join(get_app_dir(), "sam2_worker.py")
            sam2_proc = subprocess.Popen(
                [sys.executable, sam2_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            ready = sam2_proc.stdout.readline().strip()
            if ready != "READY":
                stderr = sam2_proc.stderr.read()
                raise RuntimeError(f"SAM 2 worker failed: {ready}\n{stderr}")

            self.progress.emit("SAM 2 propagating mask through video...")

            cmd = {
                "action": "process",
                "frame_dir": frame_dir,
                "mask_path": mask_path,
                "click_frame_idx": first_frame_idx,
                "output_dir": output_dir
            }

            sam2_proc.stdin.write(json.dumps(cmd) + "\n")
            sam2_proc.stdin.flush()

            response_line = sam2_proc.stdout.readline().strip()

            try:
                sam2_proc.stdin.write("QUIT\n")
                sam2_proc.stdin.flush()
                sam2_proc.terminate()
            except:
                pass

            if not response_line:
                stderr = sam2_proc.stderr.read()
                raise RuntimeError(f"No response from SAM 2.\nStderr: {stderr}")

            response = json.loads(response_line)
            if response.get("status") != "OK":
                raise RuntimeError(response.get("message", "Unknown error") +
                                 "\n" + response.get("traceback", ""))

            # Step 4: Load results
            self.progress.emit("Loading segmented frames...")
            num_loaded = 0

            for i in range(len(self.frames)):
                out_path = os.path.join(output_dir, f"{i:05d}.png")
                if os.path.exists(out_path):
                    result_img = Image.open(out_path).copy()
                    self.frame_done.emit(i, result_img)
                    num_loaded += 1

            self.finished_all.emit(num_loaded)

        except Exception as e:
            import traceback
            self.error_occurred.emit(f"{str(e)}\n\n{traceback.format_exc()}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# THUMBNAIL WIDGET
# ============================================================================

class ThumbnailWidget(QLabel):
    """Clickable thumbnail widget with drag selection support."""
    clicked = pyqtSignal(int, bool, bool)  # index, shift, ctrl
    rightClicked = pyqtSignal(int)  # right-click to deselect
    doubleClicked = pyqtSignal(int)
    dragStarted = pyqtSignal(int)  # index where drag started
    dragEntered = pyqtSignal(int)  # index mouse entered while dragging

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.setFixedSize(72, 72)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        self.setMouseTracking(True)
        self._drag_started = False
        self._press_pos = None
        self.is_selected = False
        self.is_deleted = False
        self.is_trim_start = False
        self.is_trim_end = False
        self.update_style()

    def update_style(self):
        if self.is_deleted:
            border_color = "#e74c3c"
            bg_color = "#3a2020"
        elif self.is_selected:
            border_color = "#6c5ce7"
            bg_color = "#2a2a5a"
        elif self.is_trim_start or self.is_trim_end:
            border_color = "#f39c12"
            bg_color = "#3a3520"
        else:
            border_color = "#3a3a5a"
            bg_color = "#2a2a4a"

        self.setStyleSheet(f"""
            QLabel {{
                border: 3px solid {border_color};
                border-radius: 8px;
                background-color: {bg_color};
                padding: 2px;
            }}
        """)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def set_deleted(self, deleted):
        self.is_deleted = deleted
        self.update_style()

    def set_trim_marker(self, is_start=False, is_end=False):
        self.is_trim_start = is_start
        self.is_trim_end = is_end
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_pos = event.pos()
            self._drag_started = False
            # Emit drag start immediately for drag selection
            self.dragStarted.emit(self.index)
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit(self.index)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self._press_pos is not None:
                # Check if we've moved enough to consider it a drag
                diff = event.pos() - self._press_pos
                if diff.manhattanLength() > 5:
                    self._drag_started = True
            self.dragEntered.emit(self.index)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self._drag_started:
                # It was a click, not a drag
                shift = event.modifiers() & Qt.ShiftModifier
                ctrl = event.modifiers() & Qt.ControlModifier
                self.clicked.emit(self.index, bool(shift), bool(ctrl))
            self._press_pos = None
            self._drag_started = False

    def enterEvent(self, event):
        # Check if mouse button is held (for drag selection from another thumbnail)
        if QApplication.mouseButtons() & Qt.LeftButton:
            self.dragEntered.emit(self.index)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit(self.index)


# ============================================================================
# DROP ZONE WIDGET
# ============================================================================

class DropZone(QLabel):
    """Widget that accepts drag & drop of GIF files."""
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag & Drop GIF Here\n\nor click to browse")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(200)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.gif'):
                event.acceptProposedAction()
                self.setStyleSheet(self.styleSheet() + "border-color: #6c5ce7 !important;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.gif'):
                self.fileDropped.emit(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select GIF", "", "GIF files (*.gif);;All files (*.*)"
            )
            if file_path:
                self.fileDropped.emit(file_path)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class GifBackgroundRemover(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Background Remover Pro")
        self.setGeometry(100, 100, 1400, 900)
        self.setAcceptDrops(True)

        # State
        self.original_frames = []
        self.processed_frames = []
        self.frame_durations = []
        self.deleted_frames = set()
        self.selected_frames = set()  # For multi-select
        self.last_clicked_frame = None  # For shift-click range
        self.drag_start_frame = None  # For drag selection
        self.is_dragging = False
        self.current_frame_index = 0
        self.is_playing = False
        self.gif_path = None
        self.show_processed = False
        self.thumbnails = []
        self.trim_start = 0
        self.trim_end = 0
        self.preview_bg_color = None  # None = checkerboard
        self.replacement_bg = None  # None, color tuple, or PIL Image
        self.playback_speed = 1.0

        # Caption settings
        self.caption_text = ""
        self.caption_font = "Arial"
        self.caption_size = 24
        self.caption_color = (255, 255, 255)
        self.caption_position = "bottom"  # top, center, bottom
        self.caption_stroke = True
        self.caption_stroke_color = (0, 0, 0)

        # Compression state
        self.compressed_data = None  # Holds rendered compressed bytes
        self.compressed_format = None  # "gif" or "webm"

        # Mask painting state
        self.paint_mode_active = False
        self.erase_mode_active = False
        self.last_paint_pos = None
        self.preview_scale_factor = 1.0
        self.preview_offset = (0, 0)

        # SAM 2 click mode state
        self.sam2_click_mode = False
        self.sam2_click_points = []
        self.sam2_click_labels = []

        # Resize settings
        self.export_width = 0  # 0 = original
        self.export_height = 0
        self.maintain_aspect = True

        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.play_next_frame)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        pass  # Will be handled in keyPressEvent

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Left panel - Preview
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # Preview area with drop zone
        self.preview_stack = QWidget()
        preview_layout = QVBoxLayout(self.preview_stack)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        # Drop zone (shown when no GIF loaded)
        self.drop_zone = DropZone()
        self.drop_zone.fileDropped.connect(self.load_gif)
        preview_layout.addWidget(self.drop_zone)

        # Preview label (shown when GIF loaded)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setStyleSheet("""
            background-color: #0d0d1a;
            border-radius: 12px;
        """)
        self.preview_label.setMouseTracking(True)
        self.preview_label.installEventFilter(self)
        self.preview_label.hide()
        preview_layout.addWidget(self.preview_label)

        left_panel.addWidget(self.preview_stack, 1)

        # Playback controls
        playback_group = QGroupBox("Playback")
        playback_layout = QHBoxLayout(playback_group)

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedWidth(50)
        self.btn_prev.clicked.connect(self.prev_frame)
        self.btn_prev.setToolTip("Previous frame (←)")
        playback_layout.addWidget(self.btn_prev)

        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setObjectName("primaryBtn")
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_play.setToolTip("Play/Pause (Space)")
        playback_layout.addWidget(self.btn_play)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedWidth(50)
        self.btn_next.clicked.connect(self.next_frame)
        self.btn_next.setToolTip("Next frame (→)")
        playback_layout.addWidget(self.btn_next)

        playback_layout.addSpacing(20)

        playback_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "1.5x", "2x"])
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.currentTextChanged.connect(self.on_speed_changed)
        playback_layout.addWidget(self.speed_combo)

        playback_layout.addStretch()

        self.frame_info_label = QLabel("Frame: - / -")
        self.frame_info_label.setStyleSheet("color: #9d9dff; font-family: 'Consolas';")
        playback_layout.addWidget(self.frame_info_label)

        left_panel.addWidget(playback_group)

        # Frame scrubber
        scrubber_layout = QHBoxLayout()
        self.scrubber = QSlider(Qt.Horizontal)
        self.scrubber.setMinimum(0)
        self.scrubber.setMaximum(100)
        self.scrubber.valueChanged.connect(self.on_scrub)
        scrubber_layout.addWidget(self.scrubber)
        left_panel.addLayout(scrubber_layout)

        # Thumbnail strip
        thumb_scroll = QScrollArea()
        thumb_scroll.setFixedHeight(100)
        thumb_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        thumb_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        thumb_scroll.setWidgetResizable(True)
        thumb_scroll.setStyleSheet("background-color: #0d0d1a; border-radius: 8px;")

        self.thumb_container = QWidget()
        self.thumb_layout = QHBoxLayout(self.thumb_container)
        self.thumb_layout.setSpacing(6)
        self.thumb_layout.setContentsMargins(8, 8, 8, 8)
        self.thumb_layout.setAlignment(Qt.AlignLeft)

        thumb_scroll.setWidget(self.thumb_container)
        left_panel.addWidget(thumb_scroll)

        main_layout.addLayout(left_panel, 2)

        # Right panel - Controls (scrollable)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setMinimumWidth(280)
        right_scroll.setMaximumWidth(350)

        right_widget = QWidget()
        right_panel = QVBoxLayout(right_widget)
        right_panel.setSpacing(10)

        # File operations
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout(file_group)

        self.btn_load = QPushButton("📂 Open GIF")
        self.btn_load.clicked.connect(lambda: self.drop_zone.mousePressEvent(None) if not self.original_frames else self.load_gif_dialog())
        file_layout.addWidget(self.btn_load)

        self.btn_export = QPushButton("💾 Export")
        self.btn_export.setObjectName("successBtn")
        self.btn_export.clicked.connect(self.show_export_dialog)
        file_layout.addWidget(self.btn_export)

        right_panel.addWidget(file_group)

        # Background removal
        bg_group = QGroupBox("Background Removal")
        bg_layout = QVBoxLayout(bg_group)

        # Engine selector
        engine_row = QHBoxLayout()
        engine_row.addWidget(QLabel("Engine:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems([
            "Color Key (solid backgrounds - FAST)",
            "Auto + SAM 2 (AI - fully automatic)",
            "SAM 2 (AI - click to segment)",
            "RVM (AI - temporal memory)",
            "rembg (AI - general purpose)"
        ])
        self.engine_combo.setToolTip(
            "Color Key: Instant, perfect for solid color backgrounds\n"
            "Auto + SAM 2: Fully automatic AI - rembg detects, SAM 2 propagates\n"
            "SAM 2: Manual click, then propagates to all frames\n"
            "RVM: Automatic, temporal memory for people\n"
            "rembg: Automatic, per-frame, good for cartoons"
        )
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        engine_row.addWidget(self.engine_combo)
        bg_layout.addLayout(engine_row)

        # Color Key options (shown by default since it's index 0)
        self.colorkey_options = QWidget()
        colorkey_layout = QVBoxLayout(self.colorkey_options)
        colorkey_layout.setContentsMargins(0, 5, 0, 0)

        # Color picker row
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        self.colorkey_color_btn = QPushButton("")
        self.colorkey_color_btn.setFixedSize(60, 25)
        self.colorkey_color_btn.setStyleSheet("background-color: #ffffff; border: 2px solid #3a3a5a;")
        self.colorkey_color_btn.clicked.connect(self.pick_colorkey_color)
        self.colorkey_color = (255, 255, 255)  # Default white
        color_row.addWidget(self.colorkey_color_btn)

        self.btn_auto_detect_color = QPushButton("Auto")
        self.btn_auto_detect_color.setFixedWidth(50)
        self.btn_auto_detect_color.setToolTip("Auto-detect background color from frame corners")
        self.btn_auto_detect_color.clicked.connect(self.auto_detect_bg_color)
        color_row.addWidget(self.btn_auto_detect_color)
        colorkey_layout.addLayout(color_row)

        # Threshold slider
        thresh_row = QHBoxLayout()
        thresh_row.addWidget(QLabel("Tolerance:"))
        self.colorkey_threshold = QSlider(Qt.Horizontal)
        self.colorkey_threshold.setRange(0, 100)
        self.colorkey_threshold.setValue(40)
        thresh_row.addWidget(self.colorkey_threshold)
        self.colorkey_thresh_label = QLabel("40%")
        self.colorkey_thresh_label.setFixedWidth(35)
        self.colorkey_threshold.valueChanged.connect(
            lambda v: self.colorkey_thresh_label.setText(f"{v}%")
        )
        thresh_row.addWidget(self.colorkey_thresh_label)
        colorkey_layout.addLayout(thresh_row)

        # Outer only checkbox
        self.colorkey_outer_only = QCheckBox("Only remove outer background")
        self.colorkey_outer_only.setChecked(True)
        self.colorkey_outer_only.setToolTip("Only remove colors connected to frame edges (recommended)")
        colorkey_layout.addWidget(self.colorkey_outer_only)

        self.colorkey_ai_refine = QCheckBox("AI Edge Refinement")
        self.colorkey_ai_refine.setChecked(False)
        self.colorkey_ai_refine.setToolTip("Use AI to refine edges - better quality, slightly slower")
        colorkey_layout.addWidget(self.colorkey_ai_refine)

        self.colorkey_ai_protect = QCheckBox("Protect subject with AI")
        self.colorkey_ai_protect.setChecked(False)
        self.colorkey_ai_protect.setToolTip("AI detects subject first, color key won't remove anything inside it (fixes white-on-white)")
        colorkey_layout.addWidget(self.colorkey_ai_protect)

        bg_layout.addWidget(self.colorkey_options)

        # rembg model selector (hidden by default)
        self.rembg_options = QWidget()
        rembg_layout = QVBoxLayout(self.rembg_options)
        rembg_layout.setContentsMargins(0, 5, 0, 0)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "u2net (General)",
            "u2net_human_seg (People)",
            "isnet-general-use (High Quality)",
            "isnet-anime (Anime/Cartoon)",
            "silueta (Portraits)"
        ])
        model_row.addWidget(self.model_combo)
        rembg_layout.addLayout(model_row)

        self.rembg_options.hide()
        bg_layout.addWidget(self.rembg_options)

        # Engine hint
        self.engine_hint = QLabel(
            "Instant removal of solid color backgrounds. Click 'Pick Color' or auto-detect."
        )
        self.engine_hint.setWordWrap(True)
        self.engine_hint.setStyleSheet("color: #7a7a9a;")
        bg_layout.addWidget(self.engine_hint)

        self.btn_remove_bg = QPushButton("🎨 Remove Background")
        self.btn_remove_bg.setObjectName("primaryBtn")
        self.btn_remove_bg.clicked.connect(self.remove_backgrounds)
        bg_layout.addWidget(self.btn_remove_bg)

        self.btn_toggle_view = QPushButton("👁 Toggle Original/Processed")
        self.btn_toggle_view.clicked.connect(self.toggle_view)
        bg_layout.addWidget(self.btn_toggle_view)

        self.view_status = QLabel("Viewing: Original")
        self.view_status.setStyleSheet("color: #7a7a9a;")
        bg_layout.addWidget(self.view_status)

        right_panel.addWidget(bg_group)

        # Mask Repair
        repair_group = QGroupBox("Mask Repair")
        repair_layout = QVBoxLayout(repair_group)

        # Copy mask from another frame
        copy_row = QHBoxLayout()
        self.btn_copy_mask = QPushButton("📋 Copy Mask From...")
        self.btn_copy_mask.setToolTip("Copy mask from a good frame to fix this frame")
        self.btn_copy_mask.clicked.connect(self.copy_mask_from_frame)
        copy_row.addWidget(self.btn_copy_mask)
        repair_layout.addLayout(copy_row)

        # Auto-fix outliers
        self.btn_auto_fix = QPushButton("🔧 Auto-Fix Outliers")
        self.btn_auto_fix.setToolTip("Detect and fix frames where mask suddenly changes")
        self.btn_auto_fix.clicked.connect(self.auto_fix_outliers)
        repair_layout.addWidget(self.btn_auto_fix)

        # Manual painting mode
        paint_row = QHBoxLayout()
        self.btn_paint_mode = QPushButton("🖌️ Paint Mode")
        self.btn_paint_mode.setCheckable(True)
        self.btn_paint_mode.setToolTip("Paint to restore deleted areas")
        self.btn_paint_mode.clicked.connect(self.toggle_paint_mode)
        paint_row.addWidget(self.btn_paint_mode)

        self.btn_erase_mode = QPushButton("🧹 Erase Mode")
        self.btn_erase_mode.setCheckable(True)
        self.btn_erase_mode.setToolTip("Erase to remove background areas")
        self.btn_erase_mode.clicked.connect(self.toggle_erase_mode)
        paint_row.addWidget(self.btn_erase_mode)
        repair_layout.addLayout(paint_row)

        # Brush size
        brush_row = QHBoxLayout()
        brush_row.addWidget(QLabel("Brush:"))
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setRange(5, 100)
        self.brush_size_spin.setValue(20)
        self.brush_size_spin.setSuffix("px")
        brush_row.addWidget(self.brush_size_spin)
        repair_layout.addLayout(brush_row)

        # SAM click-to-fix
        self.btn_sam_fix = QPushButton("🎯 SAM Click-to-Fix")
        self.btn_sam_fix.setToolTip("Click on subject to re-segment with SAM")
        self.btn_sam_fix.clicked.connect(self.sam_click_fix)
        repair_layout.addWidget(self.btn_sam_fix)

        right_panel.addWidget(repair_group)

        # Preview background
        preview_bg_group = QGroupBox("Preview Background")
        preview_bg_layout = QVBoxLayout(preview_bg_group)

        bg_btn_layout = QGridLayout()

        self.btn_bg_checker = QPushButton("▦")
        self.btn_bg_checker.setToolTip("Checkerboard")
        self.btn_bg_checker.setFixedSize(40, 40)
        self.btn_bg_checker.clicked.connect(lambda: self.set_preview_bg(None))
        bg_btn_layout.addWidget(self.btn_bg_checker, 0, 0)

        self.btn_bg_black = QPushButton("")
        self.btn_bg_black.setToolTip("Black")
        self.btn_bg_black.setFixedSize(40, 40)
        self.btn_bg_black.setStyleSheet("background-color: #000000; border: 2px solid #3a3a5a;")
        self.btn_bg_black.clicked.connect(lambda: self.set_preview_bg("#000000"))
        bg_btn_layout.addWidget(self.btn_bg_black, 0, 1)

        self.btn_bg_white = QPushButton("")
        self.btn_bg_white.setToolTip("White")
        self.btn_bg_white.setFixedSize(40, 40)
        self.btn_bg_white.setStyleSheet("background-color: #ffffff; border: 2px solid #3a3a5a;")
        self.btn_bg_white.clicked.connect(lambda: self.set_preview_bg("#ffffff"))
        bg_btn_layout.addWidget(self.btn_bg_white, 0, 2)

        self.btn_bg_custom = QPushButton("🎨")
        self.btn_bg_custom.setToolTip("Custom color")
        self.btn_bg_custom.setFixedSize(40, 40)
        self.btn_bg_custom.clicked.connect(self.pick_preview_bg_color)
        bg_btn_layout.addWidget(self.btn_bg_custom, 0, 3)

        preview_bg_layout.addLayout(bg_btn_layout)
        right_panel.addWidget(preview_bg_group)

        # Replace background
        replace_group = QGroupBox("Replace Background")
        replace_layout = QVBoxLayout(replace_group)

        self.btn_replace_none = QPushButton("Transparent")
        self.btn_replace_none.clicked.connect(lambda: self.set_replacement_bg(None))
        replace_layout.addWidget(self.btn_replace_none)

        self.btn_replace_color = QPushButton("Solid Color...")
        self.btn_replace_color.clicked.connect(self.pick_replacement_color)
        replace_layout.addWidget(self.btn_replace_color)

        self.btn_replace_image = QPushButton("Image...")
        self.btn_replace_image.clicked.connect(self.pick_replacement_image)
        replace_layout.addWidget(self.btn_replace_image)

        self.replace_status = QLabel("Background: Transparent")
        self.replace_status.setStyleSheet("color: #7a7a9a;")
        replace_layout.addWidget(self.replace_status)

        right_panel.addWidget(replace_group)

        # Frame operations
        frame_group = QGroupBox("Frame Operations")
        frame_layout = QVBoxLayout(frame_group)

        # Selection info and controls
        self.selection_label = QLabel("No frames selected")
        self.selection_label.setStyleSheet("color: #a0a0c0; font-style: italic;")
        frame_layout.addWidget(self.selection_label)

        select_btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.select_all_frames)
        select_btn_layout.addWidget(self.btn_select_all)

        self.btn_deselect = QPushButton("Deselect")
        self.btn_deselect.clicked.connect(self.deselect_all_frames)
        select_btn_layout.addWidget(self.btn_deselect)

        frame_layout.addLayout(select_btn_layout)

        # Delete selected button
        self.btn_delete_selected = QPushButton("🗑 Delete Selected")
        self.btn_delete_selected.setObjectName("dangerBtn")
        self.btn_delete_selected.clicked.connect(self.delete_selected_frames)
        frame_layout.addWidget(self.btn_delete_selected)

        # Single frame operations
        frame_btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton("🗑 Delete Current")
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.clicked.connect(self.delete_current_frame)
        frame_btn_layout.addWidget(self.btn_delete)

        self.btn_restore = QPushButton("↩ Restore")
        self.btn_restore.clicked.connect(self.restore_current_frame)
        frame_btn_layout.addWidget(self.btn_restore)

        frame_layout.addLayout(frame_btn_layout)

        self.btn_restore_all = QPushButton("🔄 Restore All Frames")
        self.btn_restore_all.clicked.connect(self.restore_all_frames)
        frame_layout.addWidget(self.btn_restore_all)

        # Trim controls
        trim_layout = QHBoxLayout()
        self.btn_trim_start = QPushButton("[ Set Start")
        self.btn_trim_start.clicked.connect(self.set_trim_start)
        trim_layout.addWidget(self.btn_trim_start)

        self.btn_trim_end = QPushButton("Set End ]")
        self.btn_trim_end.clicked.connect(self.set_trim_end)
        trim_layout.addWidget(self.btn_trim_end)

        frame_layout.addLayout(trim_layout)

        self.trim_label = QLabel("Trim: All frames")
        self.trim_label.setStyleSheet("color: #7a7a9a;")
        frame_layout.addWidget(self.trim_label)

        self.btn_delete_outside = QPushButton("✂ Delete Outside Trim")
        self.btn_delete_outside.setObjectName("dangerBtn")
        self.btn_delete_outside.setToolTip("Delete all frames before Start and after End")
        self.btn_delete_outside.clicked.connect(self.delete_outside_trim)
        frame_layout.addWidget(self.btn_delete_outside)

        right_panel.addWidget(frame_group)

        # Resize
        resize_group = QGroupBox("Resize")
        resize_layout = QVBoxLayout(resize_group)

        # Scale presets
        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Scale:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Original", "25%", "50%", "75%", "150%", "200%", "512x512 (Fit)", "Custom"])
        self.scale_combo.setCurrentIndex(0)
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        scale_row.addWidget(self.scale_combo)
        resize_layout.addLayout(scale_row)

        # Custom size inputs
        self.custom_size_widget = QWidget()
        custom_layout = QGridLayout(self.custom_size_widget)
        custom_layout.setContentsMargins(0, 5, 0, 0)

        custom_layout.addWidget(QLabel("W:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 4096)
        self.width_spin.setValue(480)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        custom_layout.addWidget(self.width_spin, 0, 1)

        custom_layout.addWidget(QLabel("H:"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4096)
        self.height_spin.setValue(480)
        self.height_spin.valueChanged.connect(self.on_height_changed)
        custom_layout.addWidget(self.height_spin, 0, 3)

        self.aspect_check = QCheckBox("Lock aspect")
        self.aspect_check.setChecked(True)
        custom_layout.addWidget(self.aspect_check, 1, 0, 1, 4)

        self.custom_size_widget.hide()
        resize_layout.addWidget(self.custom_size_widget)

        right_panel.addWidget(resize_group)

        # Compression
        compress_group = QGroupBox("Compress")
        compress_layout = QVBoxLayout(compress_group)

        # Target size row
        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Target:"))
        self.target_size_spin = QSpinBox()
        self.target_size_spin.setRange(16, 10240)
        self.target_size_spin.setValue(256)
        self.target_size_spin.setSuffix(" KB")
        target_row.addWidget(self.target_size_spin)
        compress_layout.addLayout(target_row)

        # Format row
        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Format:"))
        self.compress_format = QComboBox()
        self.compress_format.addItems(["GIF", "WebM"])
        format_row.addWidget(self.compress_format)
        compress_layout.addLayout(format_row)

        # Render button
        self.btn_render_compressed = QPushButton("Render Compressed")
        self.btn_render_compressed.clicked.connect(self.render_compressed)
        compress_layout.addWidget(self.btn_render_compressed)

        # Size result label
        self.compress_result_label = QLabel("")
        self.compress_result_label.setWordWrap(True)
        compress_layout.addWidget(self.compress_result_label)

        # Save compressed button (hidden until rendered)
        self.btn_save_compressed = QPushButton("Save Compressed File")
        self.btn_save_compressed.clicked.connect(self.save_compressed)
        self.btn_save_compressed.setEnabled(False)
        compress_layout.addWidget(self.btn_save_compressed)

        right_panel.addWidget(compress_group)

        # Caption
        caption_group = QGroupBox("Caption")
        caption_layout = QVBoxLayout(caption_group)

        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Enter caption text...")
        self.caption_input.textChanged.connect(self.on_caption_changed)
        caption_layout.addWidget(self.caption_input)

        # Font and size row
        font_row = QHBoxLayout()
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Impact", "Helvetica", "Times New Roman", "Comic Sans MS", "Verdana", "Georgia"])
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        font_row.addWidget(self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 120)
        self.font_size_spin.setValue(24)
        self.font_size_spin.setSuffix("px")
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        font_row.addWidget(self.font_size_spin)

        caption_layout.addLayout(font_row)

        # Position and color row
        style_row = QHBoxLayout()

        self.position_combo = QComboBox()
        self.position_combo.addItems(["Top", "Center", "Bottom"])
        self.position_combo.setCurrentIndex(2)
        self.position_combo.currentTextChanged.connect(self.on_position_changed)
        style_row.addWidget(self.position_combo)

        self.caption_color_btn = QPushButton("Color")
        self.caption_color_btn.setFixedWidth(60)
        self.caption_color_btn.setStyleSheet("background-color: #ffffff;")
        self.caption_color_btn.clicked.connect(self.pick_caption_color)
        style_row.addWidget(self.caption_color_btn)

        self.stroke_check = QCheckBox("Outline")
        self.stroke_check.setChecked(True)
        self.stroke_check.stateChanged.connect(self.on_stroke_changed)
        style_row.addWidget(self.stroke_check)

        caption_layout.addLayout(style_row)

        right_panel.addWidget(caption_group)

        right_panel.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        right_panel.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Ready - Drop a GIF to get started")
        self.status_label.setStyleSheet("color: #7a7a9a; padding: 10px;")
        self.status_label.setWordWrap(True)
        right_panel.addWidget(self.status_label)

        right_scroll.setWidget(right_widget)
        main_layout.addWidget(right_scroll, 1)

    def load_gif_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select GIF", "", "GIF files (*.gif);;All files (*.*)"
        )
        if file_path:
            self.load_gif(file_path)

    def load_gif(self, file_path):
        self.gif_path = file_path
        self.original_frames = []
        self.processed_frames = []
        self.frame_durations = []
        self.deleted_frames = set()
        self.selected_frames = set()
        self.last_clicked_frame = None
        self.current_frame_index = 0
        self.show_processed = False
        self.is_playing = False
        self.play_timer.stop()
        self.btn_play.setText("▶ Play")
        self.trim_start = 0

        try:
            gif = Image.open(file_path)

            for frame in ImageSequence.Iterator(gif):
                frame_rgba = frame.convert("RGBA")
                self.original_frames.append(frame_rgba.copy())
                self.processed_frames.append(None)
                duration = frame.info.get("duration", 100)
                self.frame_durations.append(duration)

            self.trim_end = len(self.original_frames) - 1
            self.scrubber.setMaximum(len(self.original_frames) - 1)
            self.update_thumbnails()
            self.show_frame(0)

            # Switch from drop zone to preview
            self.drop_zone.hide()
            self.preview_label.show()

            self.status_label.setText(f"Loaded: {os.path.basename(file_path)} ({len(self.original_frames)} frames)")
            self.update_trim_label()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load GIF: {str(e)}")

    def update_thumbnails(self):
        for thumb in self.thumbnails:
            thumb.deleteLater()
        self.thumbnails = []

        for i, frame in enumerate(self.original_frames):
            thumb = frame.copy()
            thumb.thumbnail((60, 60), Image.Resampling.LANCZOS)

            checker = create_checkerboard(thumb.width, thumb.height, 5)
            if thumb.mode == "RGBA":
                checker.paste(thumb, mask=thumb.split()[3])
            else:
                checker.paste(thumb)

            pixmap = pil_to_qpixmap(checker.convert("RGBA"))

            widget = ThumbnailWidget(i)
            widget.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            widget.clicked.connect(self.on_thumbnail_clicked)
            widget.rightClicked.connect(self.on_thumbnail_right_clicked)
            widget.dragStarted.connect(self.on_thumbnail_drag_start)
            widget.dragEntered.connect(self.on_thumbnail_drag_move)

            self.thumb_layout.addWidget(widget)
            self.thumbnails.append(widget)

        self.update_thumbnail_highlights()

    def update_thumbnail_highlights(self):
        for i, thumb in enumerate(self.thumbnails):
            # Show selected if in selected_frames OR if it's the current frame (with no multi-select)
            is_selected = i in self.selected_frames or (len(self.selected_frames) == 0 and i == self.current_frame_index)
            thumb.set_selected(is_selected)
            thumb.set_deleted(i in self.deleted_frames)
            thumb.set_trim_marker(i == self.trim_start, i == self.trim_end)

    def on_thumbnail_clicked(self, index, shift=False, ctrl=False):
        """Handle thumbnail click with multi-select support."""
        if shift and self.last_clicked_frame is not None:
            # Shift+click: select range
            start = min(self.last_clicked_frame, index)
            end = max(self.last_clicked_frame, index)
            for i in range(start, end + 1):
                self.selected_frames.add(i)
        elif ctrl:
            # Ctrl+click: toggle selection
            if index in self.selected_frames:
                self.selected_frames.discard(index)
            else:
                self.selected_frames.add(index)
        else:
            # Normal click: clear selection and select just this one
            self.selected_frames.clear()
            self.selected_frames.add(index)

        self.last_clicked_frame = index
        self.update_thumbnail_selection()
        self.update_selection_label()
        self.show_frame(index)

    def update_thumbnail_selection(self):
        """Update thumbnail visual selection state."""
        for thumb in self.thumbnails:
            thumb.set_selected(thumb.index in self.selected_frames)

    def update_selection_label(self):
        """Update the selection count label."""
        count = len(self.selected_frames)
        if count == 0:
            self.selection_label.setText("No frames selected")
        elif count == 1:
            self.selection_label.setText("1 frame selected")
        else:
            self.selection_label.setText(f"{count} frames selected")

    def on_thumbnail_right_clicked(self, index):
        """Right-click to deselect a frame."""
        self.selected_frames.discard(index)
        self.update_thumbnail_selection()
        self.update_selection_label()

    def on_thumbnail_drag_start(self, index):
        """Start drag selection."""
        self.is_dragging = True
        self.drag_start_frame = index
        self.selected_frames.clear()
        self.selected_frames.add(index)
        self.update_thumbnail_selection()
        self.update_selection_label()

    def on_thumbnail_drag_move(self, index):
        """Update selection during drag."""
        if not self.is_dragging or self.drag_start_frame is None:
            return

        # Select range from drag start to current
        start = min(self.drag_start_frame, index)
        end = max(self.drag_start_frame, index)
        self.selected_frames = set(range(start, end + 1))
        self.update_thumbnail_selection()
        self.update_selection_label()

    def mouseReleaseEvent(self, event):
        """End drag selection."""
        if self.is_dragging:
            self.is_dragging = False
            self.last_clicked_frame = self.drag_start_frame
        super().mouseReleaseEvent(event)

    def show_frame(self, index):
        if not self.original_frames or index < 0 or index >= len(self.original_frames):
            return

        self.current_frame_index = index
        self.scrubber.blockSignals(True)
        self.scrubber.setValue(index)
        self.scrubber.blockSignals(False)

        # Choose frame to display
        if self.show_processed and self.processed_frames[index] is not None:
            frame = self.processed_frames[index].copy()
            self.view_status.setText("Viewing: Processed")
        else:
            frame = self.original_frames[index].copy()
            self.view_status.setText("Viewing: Original")

        # Apply replacement background if set
        if self.replacement_bg is not None and self.show_processed and self.processed_frames[index] is not None:
            if isinstance(self.replacement_bg, tuple):
                bg = Image.new("RGBA", frame.size, self.replacement_bg + (255,))
            else:
                bg = self.replacement_bg.resize(frame.size, Image.Resampling.LANCZOS).convert("RGBA")
            bg.paste(frame, mask=frame.split()[3] if frame.mode == "RGBA" else None)
            frame = bg

        # Scale to fit preview
        preview_width = self.preview_label.width() - 20
        preview_height = self.preview_label.height() - 20

        if preview_width <= 0:
            preview_width = 640
        if preview_height <= 0:
            preview_height = 480

        frame_ratio = frame.width / frame.height
        preview_ratio = preview_width / preview_height

        if frame_ratio > preview_ratio:
            new_width = min(preview_width, frame.width)
            new_height = int(new_width / frame_ratio)
        else:
            new_height = min(preview_height, frame.height)
            new_width = int(new_height * frame_ratio)

        display_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Apply caption
        if self.caption_text:
            display_frame = self.draw_caption(display_frame)

        # Create background
        if self.preview_bg_color is None:
            bg = create_checkerboard(new_width, new_height)
        else:
            bg = create_solid_background(new_width, new_height, self.preview_bg_color)

        if display_frame.mode == "RGBA":
            bg.paste(display_frame, mask=display_frame.split()[3])
        else:
            bg.paste(display_frame)

        pixmap = pil_to_qpixmap(bg.convert("RGBA"))

        # Draw X on deleted frames
        if index in self.deleted_frames:
            painter = QPainter(pixmap)
            pen = painter.pen()
            pen.setColor(QColor(231, 76, 60))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(0, 0, pixmap.width(), pixmap.height())
            painter.drawLine(pixmap.width(), 0, 0, pixmap.height())
            painter.end()

        self.preview_label.setPixmap(pixmap)

        # Update info
        status_parts = []
        if index in self.deleted_frames:
            status_parts.append("DELETED")
        if self.processed_frames[index] is not None:
            status_parts.append("✓")
        status_str = f" [{', '.join(status_parts)}]" if status_parts else ""

        self.frame_info_label.setText(f"Frame: {index + 1} / {len(self.original_frames)}{status_str}")
        self.update_thumbnail_highlights()

    def on_scrub(self, value):
        if value != self.current_frame_index:
            self.show_frame(value)

    def prev_frame(self):
        if self.original_frames and self.current_frame_index > 0:
            self.show_frame(self.current_frame_index - 1)

    def next_frame(self):
        if self.original_frames and self.current_frame_index < len(self.original_frames) - 1:
            self.show_frame(self.current_frame_index + 1)

    def on_speed_changed(self, text):
        speed_map = {"0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "1.5x": 1.5, "2x": 2.0}
        self.playback_speed = speed_map.get(text, 1.0)

    def toggle_play(self):
        if not self.original_frames:
            return

        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.setText("⏸ Pause")
            self.play_next_frame()
        else:
            self.btn_play.setText("▶ Play")
            self.play_timer.stop()

    def play_next_frame(self):
        if not self.is_playing:
            return

        next_index = self.current_frame_index + 1
        while next_index in self.deleted_frames:
            next_index += 1

        if next_index > self.trim_end:
            next_index = self.trim_start
            while next_index in self.deleted_frames and next_index <= self.trim_end:
                next_index += 1

        self.show_frame(next_index)

        duration = int(self.frame_durations[self.current_frame_index] / self.playback_speed)
        self.play_timer.start(max(duration, 10))

    def delete_current_frame(self):
        if not self.original_frames:
            return

        active_frames = len(self.original_frames) - len(self.deleted_frames)
        if active_frames <= 1:
            QMessageBox.warning(self, "Warning", "Cannot delete the last remaining frame!")
            return

        self.deleted_frames.add(self.current_frame_index)
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"Frame {self.current_frame_index + 1} marked for deletion")

    def restore_current_frame(self):
        if self.current_frame_index in self.deleted_frames:
            self.deleted_frames.remove(self.current_frame_index)
            self.show_frame(self.current_frame_index)
            self.status_label.setText(f"Frame {self.current_frame_index + 1} restored")

    def restore_all_frames(self):
        self.deleted_frames.clear()
        self.show_frame(self.current_frame_index)
        self.status_label.setText("All frames restored")

    def select_all_frames(self):
        """Select all frames."""
        if not self.original_frames:
            return
        self.selected_frames = set(range(len(self.original_frames)))
        self.update_thumbnail_selection()
        self.update_selection_label()

    def deselect_all_frames(self):
        """Clear frame selection."""
        self.selected_frames.clear()
        self.update_thumbnail_selection()
        self.update_selection_label()

    def delete_selected_frames(self):
        """Delete all selected frames."""
        if not self.selected_frames:
            QMessageBox.warning(self, "Warning", "No frames selected!\n\nTip: Shift+click for range, Ctrl+click to add/remove")
            return

        # Check if we'd delete all frames
        remaining = len(self.original_frames) - len(self.deleted_frames | self.selected_frames)
        if remaining < 1:
            QMessageBox.warning(self, "Warning", "Cannot delete all frames! At least one must remain.")
            return

        # Delete selected frames
        count = len(self.selected_frames - self.deleted_frames)
        self.deleted_frames.update(self.selected_frames)
        self.selected_frames.clear()

        self.update_thumbnail_selection()
        self.update_selection_label()
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"{count} frames marked for deletion")

    def set_trim_start(self):
        if self.original_frames:
            self.trim_start = self.current_frame_index
            if self.trim_start > self.trim_end:
                self.trim_end = len(self.original_frames) - 1
            self.update_trim_label()
            self.update_thumbnail_highlights()

    def set_trim_end(self):
        if self.original_frames:
            self.trim_end = self.current_frame_index
            if self.trim_end < self.trim_start:
                self.trim_start = 0
            self.update_trim_label()
            self.update_thumbnail_highlights()

    def update_trim_label(self):
        if self.original_frames:
            total = self.trim_end - self.trim_start + 1
            self.trim_label.setText(f"Trim: Frame {self.trim_start + 1} to {self.trim_end + 1} ({total} frames)")

    def delete_outside_trim(self):
        """Delete all frames outside the trim range."""
        if not self.original_frames:
            return

        # Count frames that would be deleted
        before = self.trim_start
        after = len(self.original_frames) - 1 - self.trim_end
        total_delete = before + after

        if total_delete == 0:
            QMessageBox.information(self, "Info", "Trim is set to all frames - nothing to delete.")
            return

        # Mark frames for deletion
        for i in range(0, self.trim_start):
            self.deleted_frames.add(i)
        for i in range(self.trim_end + 1, len(self.original_frames)):
            self.deleted_frames.add(i)

        self.update_thumbnail_highlights()
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"Deleted {total_delete} frames outside trim range")

    def set_preview_bg(self, color):
        self.preview_bg_color = color
        self.show_frame(self.current_frame_index)

    def pick_preview_bg_color(self):
        color = QColorDialog.getColor(Qt.white, self, "Choose Preview Background")
        if color.isValid():
            self.set_preview_bg(color.name())

    def set_replacement_bg(self, bg):
        self.replacement_bg = bg
        if bg is None:
            self.replace_status.setText("Background: Transparent")
        elif isinstance(bg, tuple):
            self.replace_status.setText(f"Background: Color #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}")
        else:
            self.replace_status.setText("Background: Image")
        self.show_frame(self.current_frame_index)

    def pick_replacement_color(self):
        color = QColorDialog.getColor(Qt.green, self, "Choose Replacement Background")
        if color.isValid():
            self.set_replacement_bg((color.red(), color.green(), color.blue()))

    def pick_replacement_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Image", "",
            "Image files (*.png *.jpg *.jpeg *.bmp);;All files (*.*)"
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.set_replacement_bg(img)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load image: {str(e)}")

    def toggle_view(self):
        if not any(self.processed_frames):
            QMessageBox.information(self, "Info", "No processed frames yet. Run 'Remove Background' first.")
            return

        self.show_processed = not self.show_processed
        self.show_frame(self.current_frame_index)

    # -------------------------------------------------------------------------
    # Resize handlers
    # -------------------------------------------------------------------------

    def on_scale_changed(self, text):
        if text == "Custom":
            self.custom_size_widget.show()
            if self.original_frames:
                frame = self.original_frames[0]
                self.width_spin.setValue(frame.width)
                self.height_spin.setValue(frame.height)
        else:
            self.custom_size_widget.hide()

    def on_width_changed(self, value):
        if self.aspect_check.isChecked() and self.original_frames:
            frame = self.original_frames[0]
            ratio = frame.height / frame.width
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(int(value * ratio))
            self.height_spin.blockSignals(False)

    def on_height_changed(self, value):
        if self.aspect_check.isChecked() and self.original_frames:
            frame = self.original_frames[0]
            ratio = frame.width / frame.height
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(int(value * ratio))
            self.width_spin.blockSignals(False)

    # -------------------------------------------------------------------------
    # Caption handlers
    # -------------------------------------------------------------------------

    def on_caption_changed(self, text):
        self.caption_text = text
        self.show_frame(self.current_frame_index)

    def on_font_changed(self, font):
        self.caption_font = font
        self.show_frame(self.current_frame_index)

    def on_font_size_changed(self, size):
        self.caption_size = size
        self.show_frame(self.current_frame_index)

    def on_position_changed(self, position):
        self.caption_position = position.lower()
        self.show_frame(self.current_frame_index)

    def on_stroke_changed(self, state):
        self.caption_stroke = state == Qt.Checked
        self.show_frame(self.current_frame_index)

    def on_engine_changed(self, index):
        # 0: Color Key, 1: Auto+SAM2, 2: SAM 2 click, 3: RVM, 4: rembg
        self.colorkey_options.setVisible(index == 0)
        self.rembg_options.setVisible(index == 4)
        if index == 0:  # Color Key
            self.engine_hint.setText(
                "Instant removal of solid color backgrounds. Click 'Pick Color' or auto-detect."
            )
        elif index == 1:  # Auto + SAM 2
            self.engine_hint.setText(
                "Fully automatic: rembg detects subject, SAM 2 propagates with temporal consistency."
            )
        elif index == 2:  # SAM 2 click
            self.engine_hint.setText(
                "SAM 2: Click on subject once, it segments the entire video automatically."
            )
        elif index == 3:  # RVM
            self.engine_hint.setText(
                "RVM maintains temporal memory across frames - best for people in videos."
            )
        else:  # rembg
            self.engine_hint.setText(
                "rembg processes each frame independently - better for cartoons/objects."
            )

    def pick_caption_color(self):
        color = QColorDialog.getColor(
            QColor(*self.caption_color), self, "Choose Caption Color"
        )
        if color.isValid():
            self.caption_color = (color.red(), color.green(), color.blue())
            self.caption_color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.show_frame(self.current_frame_index)

    def draw_caption(self, image):
        """Draw caption text on an image."""
        if not self.caption_text:
            return image

        img = image.copy()
        draw = ImageDraw.Draw(img)

        # Try to load font
        try:
            font = ImageFont.truetype(f"{self.caption_font}.ttf", self.caption_size)
        except:
            try:
                # Try Windows font path
                font = ImageFont.truetype(f"C:/Windows/Fonts/{self.caption_font}.ttf", self.caption_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", self.caption_size)
                except:
                    font = ImageFont.load_default()

        # Get text size
        bbox = draw.textbbox((0, 0), self.caption_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        x = (img.width - text_width) // 2

        if self.caption_position == "top":
            y = 10
        elif self.caption_position == "center":
            y = (img.height - text_height) // 2
        else:  # bottom
            y = img.height - text_height - 20

        # Draw stroke/outline
        if self.caption_stroke:
            stroke_color = self.caption_stroke_color
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), self.caption_text, font=font, fill=stroke_color)

        # Draw main text
        draw.text((x, y), self.caption_text, font=font, fill=self.caption_color)

        return img

    def remove_backgrounds(self):
        if not self.original_frames:
            QMessageBox.warning(self, "Warning", "Load a GIF first!")
            return

        engine_index = self.engine_combo.currentIndex()

        # Color Key - instant, no AI
        if engine_index == 0:
            self.run_colorkey_removal()
            return

        # Auto + SAM 2 hybrid - fully automatic
        if engine_index == 1:
            self.run_auto_sam2_hybrid()
            return

        # SAM 2 click mode - needs user input first
        if engine_index == 2:
            self.start_sam2_click_mode()
            return

        # RVM or rembg - automatic processing
        if engine_index == 3:  # RVM
            worker_script = os.path.join(get_app_dir(), "rvm_only_worker.py")
            engine_name = "RVM"
            model = None
        else:  # rembg (index 4)
            worker_script = os.path.join(get_app_dir(), "rembg_only_worker.py")
            engine_name = "rembg"
            model = self.model_combo.currentText().split(" ")[0]

        worker_command = [sys.executable, worker_script]

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.original_frames))
        self.progress_bar.setFormat(f"Starting {engine_name}...")

        self.worker = BackgroundRemovalThread(
            self.original_frames, self.deleted_frames, worker_command, model=model
        )
        self.worker.progress.connect(self.on_removal_progress)
        self.worker.frame_done.connect(self.on_frame_processed)
        self.worker.finished_all.connect(self.on_removal_complete)
        self.worker.error_occurred.connect(self.on_removal_error)
        self.worker.start()

    def on_removal_progress(self, current, total, status):
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(status)
        self.status_label.setText(status)

    def on_frame_processed(self, index, result):
        self.processed_frames[index] = result

    def on_removal_complete(self):
        self.progress_bar.setVisible(False)
        self.show_processed = True
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"Background removal complete! ({len(self.original_frames)} frames)")

    def on_removal_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Background removal failed:\n\n{error_msg}")

    def show_export_dialog(self):
        if not self.original_frames:
            QMessageBox.warning(self, "Warning", "Load a GIF first!")
            return

        # Create export menu
        menu = QMenu(self)

        action_gif = menu.addAction("Export as GIF")
        action_gif.triggered.connect(lambda: self.export_format("gif"))

        action_webp = menu.addAction("Export as WebP")
        action_webp.triggered.connect(lambda: self.export_format("webp"))

        action_apng = menu.addAction("Export as APNG")
        action_apng.triggered.connect(lambda: self.export_format("apng"))

        action_webm = menu.addAction("Export as WebM (video)")
        action_webm.triggered.connect(lambda: self.export_format("webm"))

        menu.addSeparator()

        action_frames = menu.addAction("Export Frames as ZIP")
        action_frames.triggered.connect(self.export_frames_zip)

        menu.exec_(self.btn_export.mapToGlobal(self.btn_export.rect().bottomLeft()))

    def get_export_frames(self):
        """Get frames for export, applying trim, deletions, scale, and captions."""
        use_processed = self.show_processed and any(self.processed_frames)

        frames = []
        durations = []

        # Determine target size
        scale_text = self.scale_combo.currentText()
        fit_size = None  # For "Fit" modes that preserve aspect ratio
        if scale_text == "Original":
            target_size = None  # Keep original
        elif scale_text == "Custom":
            target_size = (self.width_spin.value(), self.height_spin.value())
        elif scale_text == "512x512 (Fit)":
            target_size = None  # Will calculate per-frame to preserve aspect
            fit_size = 512
        else:
            scale = int(scale_text.replace("%", "")) / 100
            if self.original_frames:
                orig = self.original_frames[0]
                target_size = (int(orig.width * scale), int(orig.height * scale))
            else:
                target_size = None

        for i in range(self.trim_start, self.trim_end + 1):
            if i in self.deleted_frames:
                continue

            if use_processed and self.processed_frames[i] is not None:
                frame = self.processed_frames[i].copy()

                # Apply replacement background
                if self.replacement_bg is not None:
                    if isinstance(self.replacement_bg, tuple):
                        bg = Image.new("RGBA", frame.size, self.replacement_bg + (255,))
                    else:
                        bg = self.replacement_bg.resize(frame.size, Image.Resampling.LANCZOS).convert("RGBA")
                    bg.paste(frame, mask=frame.split()[3] if frame.mode == "RGBA" else None)
                    frame = bg
            else:
                frame = self.original_frames[i].copy()

            # Apply resize
            if fit_size is not None:
                # Fit within fit_size x fit_size while preserving aspect ratio
                w, h = frame.size
                if w > h:
                    new_w = fit_size
                    new_h = int(h * fit_size / w)
                else:
                    new_h = fit_size
                    new_w = int(w * fit_size / h)
                frame = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
            elif target_size is not None:
                frame = frame.resize(target_size, Image.Resampling.LANCZOS)

            # Apply caption
            if self.caption_text:
                frame = self.draw_caption(frame)

            frames.append(frame)
            durations.append(self.frame_durations[i])

        return frames, durations

    def export_format(self, format_type):
        frames, durations = self.get_export_frames()

        if not frames:
            QMessageBox.critical(self, "Error", "No frames to export!")
            return

        default_name = "output"
        if self.gif_path:
            default_name = os.path.splitext(os.path.basename(self.gif_path))[0] + "_edited"

        ext_map = {"gif": ".gif", "webp": ".webp", "apng": ".png", "webm": ".webm"}
        filter_map = {
            "gif": "GIF files (*.gif)",
            "webp": "WebP files (*.webp)",
            "apng": "PNG files (*.png)",
            "webm": "WebM files (*.webm)"
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export {format_type.upper()}",
            default_name + ext_map[format_type],
            filter_map[format_type]
        )

        if not file_path:
            return

        try:
            if format_type == "gif":
                self.export_gif(file_path, frames, durations)
            elif format_type == "webp":
                self.export_webp(file_path, frames, durations)
            elif format_type == "apng":
                self.export_apng(file_path, frames, durations)
            elif format_type == "webm":
                self.export_webm(file_path, frames, durations)

            self.status_label.setText(f"Exported: {os.path.basename(file_path)}")
            QMessageBox.information(self, "Success", f"Exported successfully!\n\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_gif(self, file_path, frames, durations):
        export_frames = []
        for frame in frames:
            if frame.mode == "RGBA":
                alpha = frame.split()[3]
                frame_p = frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                frame_p.paste(255, mask)
                frame_p.info["transparency"] = 255
                export_frames.append(frame_p)
            else:
                export_frames.append(frame.convert("P", palette=Image.ADAPTIVE))

        export_frames[0].save(
            file_path,
            save_all=True,
            append_images=export_frames[1:],
            duration=durations,
            loop=0,
            disposal=2,
            transparency=255
        )

    def export_webp(self, file_path, frames, durations):
        frames[0].save(
            file_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            lossless=True
        )

    def export_apng(self, file_path, frames, durations):
        frames[0].save(
            file_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )

    def export_webm(self, file_path, frames, durations):
        """Export as WebM video with transparency support."""
        import subprocess

        # Create temp directory for frames
        temp_dir = tempfile.mkdtemp(prefix="webm_export_")

        try:
            # Calculate average frame rate from durations
            avg_duration = sum(durations) / len(durations)  # ms
            fps = 1000 / avg_duration if avg_duration > 0 else 10

            # Save frames as PNG (with alpha)
            for i, frame in enumerate(frames):
                frame_path = os.path.join(temp_dir, f"{i:05d}.png")
                frame.save(frame_path, "PNG")

            # Build ffmpeg command for WebM with alpha
            input_pattern = os.path.join(temp_dir, "%05d.png")

            cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", input_pattern,
                "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p",  # With alpha channel
                "-b:v", "2M",
                "-auto-alt-ref", "0",
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # Try without alpha if it fails
                cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(fps),
                    "-i", input_pattern,
                    "-c:v", "libvpx-vp9",
                    "-pix_fmt", "yuv420p",
                    "-b:v", "2M",
                    file_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    raise RuntimeError(f"ffmpeg failed: {result.stderr}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def export_telegram_compressed(self):
        """Export GIF compressed to <256KB for Telegram."""
        frames, durations = self.get_export_frames()

        if not frames:
            QMessageBox.critical(self, "Error", "No frames to export!")
            return

        default_name = "output_telegram"
        if self.gif_path:
            default_name = os.path.splitext(os.path.basename(self.gif_path))[0] + "_telegram"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Compressed GIF for Telegram",
            default_name + ".gif",
            "GIF files (*.gif)"
        )

        if not file_path:
            return

        target_size = 256 * 1024  # 256KB in bytes

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setFormat("Compressing...")
            QApplication.processEvents()

            # Try progressively more aggressive compression
            result_frames = frames
            result_durations = durations

            for attempt in range(10):
                # Calculate scale factor based on attempt
                if attempt < 5:
                    # First 5 attempts: reduce resolution
                    scale = 1.0 - (attempt * 0.15)  # 1.0, 0.85, 0.70, 0.55, 0.40
                    skip = 1
                    colors = 256
                else:
                    # Next attempts: also reduce frames and colors
                    scale = 0.4
                    skip = 1 + (attempt - 5)  # Skip every 2nd, 3rd, 4th frame
                    colors = max(32, 256 - (attempt - 5) * 48)

                # Apply scaling
                if scale < 1.0:
                    orig_size = frames[0].size
                    new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
                    new_size = (max(16, new_size[0]), max(16, new_size[1]))
                    result_frames = [f.resize(new_size, Image.Resampling.LANCZOS) for f in frames]
                else:
                    result_frames = frames

                # Apply frame skipping
                if skip > 1:
                    result_frames = result_frames[::skip]
                    result_durations = [d * skip for d in durations[::skip]]
                else:
                    result_durations = durations

                # Convert to GIF palette with limited colors
                export_frames = []
                for frame in result_frames:
                    if frame.mode == "RGBA":
                        alpha = frame.split()[3]
                        frame_p = frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=min(colors, 255))
                        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                        frame_p.paste(255, mask)
                        frame_p.info["transparency"] = 255
                        export_frames.append(frame_p)
                    else:
                        export_frames.append(frame.convert("P", palette=Image.ADAPTIVE, colors=min(colors, 255)))

                # Save to buffer to check size
                buffer = io.BytesIO()
                export_frames[0].save(
                    buffer,
                    format="GIF",
                    save_all=True,
                    append_images=export_frames[1:],
                    duration=result_durations,
                    loop=0,
                    disposal=2,
                    transparency=255,
                    optimize=True
                )

                size = buffer.tell()
                self.progress_bar.setFormat(f"Attempt {attempt + 1}: {size // 1024}KB (target: <256KB)")
                QApplication.processEvents()

                if size <= target_size:
                    # Success! Write to file
                    with open(file_path, "wb") as f:
                        f.write(buffer.getvalue())

                    self.progress_bar.setVisible(False)
                    final_size = os.path.getsize(file_path)
                    info = f"Size: {final_size // 1024}KB"
                    if scale < 1.0:
                        info += f", Scale: {int(scale * 100)}%"
                    if skip > 1:
                        info += f", Frames: {len(result_frames)}/{len(frames)}"

                    self.status_label.setText(f"Exported: {os.path.basename(file_path)} ({info})")
                    QMessageBox.information(self, "Success",
                        f"Compressed successfully!\n\n{file_path}\n\n{info}")
                    return

            # If we get here, couldn't compress enough
            self.progress_bar.setVisible(False)

            # Save anyway with best effort
            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())

            final_size = os.path.getsize(file_path)
            QMessageBox.warning(self, "Warning",
                f"Could not compress below 256KB.\n"
                f"Final size: {final_size // 1024}KB\n\n"
                f"Try trimming frames or using a smaller source.")

        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"Compression failed: {str(e)}")

    def render_compressed(self):
        """Render compressed preview and show resulting size."""
        frames, durations = self.get_export_frames()

        if not frames:
            QMessageBox.warning(self, "Warning", "Load a GIF first!")
            return

        target_kb = self.target_size_spin.value()
        target_size = target_kb * 1024
        fmt = self.compress_format.currentText().lower()

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setFormat("Compressing...")
        self.compress_result_label.setText("Rendering...")
        self.btn_save_compressed.setEnabled(False)
        QApplication.processEvents()

        try:
            best_data = None
            best_scale = 1.0
            best_size = 0

            # For WebM, first fit to 512x512 (Telegram requirement)
            orig_size = frames[0].size
            if fmt == "webm":
                # Fit into 512x512 maintaining aspect ratio
                w, h = orig_size
                if w >= h:
                    base_size = (512, int(512 * h / w))
                else:
                    base_size = (int(512 * w / h), 512)
            else:
                base_size = orig_size

            # Try progressively smaller resolutions
            for attempt, scale in enumerate([1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1]):
                self.progress_bar.setFormat(f"Trying {int(scale * 100)}% scale...")
                QApplication.processEvents()

                # Scale frames from base size
                new_size = (max(16, int(base_size[0] * scale)), max(16, int(base_size[1] * scale)))
                scaled_frames = [f.resize(new_size, Image.Resampling.LANCZOS) for f in frames]

                # Render to buffer
                buffer = io.BytesIO()

                if fmt == "gif":
                    # Convert to GIF palette
                    export_frames = []
                    for frame in scaled_frames:
                        if frame.mode == "RGBA":
                            alpha = frame.split()[3]
                            frame_p = frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
                            mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                            frame_p.paste(255, mask)
                            frame_p.info["transparency"] = 255
                            export_frames.append(frame_p)
                        else:
                            export_frames.append(frame.convert("P", palette=Image.ADAPTIVE, colors=255))

                    export_frames[0].save(
                        buffer,
                        format="GIF",
                        save_all=True,
                        append_images=export_frames[1:],
                        duration=durations,
                        loop=0,
                        disposal=2,
                        transparency=255,
                        optimize=True
                    )
                else:  # webm
                    buffer = self._render_webm_to_buffer(scaled_frames, durations)

                size = len(buffer.getvalue()) if hasattr(buffer, 'getvalue') else buffer.tell()
                buffer.seek(0)

                # Keep track of best result
                if best_data is None or size <= target_size or (best_size > target_size and size < best_size):
                    best_data = buffer.getvalue()
                    best_scale = scale
                    best_size = size

                # Stop if we hit target
                if size <= target_size:
                    break

            # Store result
            self.compressed_data = best_data
            self.compressed_format = fmt

            # Update UI
            size_kb = len(best_data) / 1024
            new_w = int(base_size[0] * best_scale)
            new_h = int(base_size[1] * best_scale)

            status = "OK" if size_kb <= target_kb else "Over target"
            telegram_note = ""
            if fmt == "webm":
                telegram_note = "\n(512x512 fit for Telegram)"
            self.compress_result_label.setText(
                f"{status}: {size_kb:.1f} KB\n"
                f"Resolution: {new_w}x{new_h}{telegram_note}"
            )

            if size_kb <= target_kb:
                self.compress_result_label.setStyleSheet("color: green;")
            else:
                self.compress_result_label.setStyleSheet("color: orange;")

            self.btn_save_compressed.setEnabled(True)

        except Exception as e:
            self.compress_result_label.setText(f"Error: {str(e)}")
            self.compress_result_label.setStyleSheet("color: red;")

        finally:
            self.progress_bar.setVisible(False)

    def _render_webm_to_buffer(self, frames, durations):
        """Render frames to WebM and return bytes."""
        import subprocess

        temp_dir = tempfile.mkdtemp(prefix="webm_compress_")
        output_file = os.path.join(temp_dir, "output.webm")

        try:
            # Calculate fps
            avg_duration = sum(durations) / len(durations)
            fps = 1000 / avg_duration if avg_duration > 0 else 10

            # Save frames
            for i, frame in enumerate(frames):
                frame.save(os.path.join(temp_dir, f"{i:05d}.png"), "PNG")

            # Run ffmpeg
            cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", os.path.join(temp_dir, "%05d.png"),
                "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p",
                "-b:v", "500K",
                "-auto-alt-ref", "0",
                output_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # Try without alpha
                cmd[cmd.index("yuva420p")] = "yuv420p"
                subprocess.run(cmd, capture_output=True, text=True)

            # Read result
            with open(output_file, "rb") as f:
                data = f.read()

            buffer = io.BytesIO(data)
            return buffer

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def save_compressed(self):
        """Save the rendered compressed file."""
        if not self.compressed_data:
            QMessageBox.warning(self, "Warning", "Render first!")
            return

        ext = "gif" if self.compressed_format == "gif" else "webm"
        default_name = "compressed"
        if self.gif_path:
            default_name = os.path.splitext(os.path.basename(self.gif_path))[0] + "_compressed"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed File",
            default_name + f".{ext}",
            f"{ext.upper()} files (*.{ext})"
        )

        if not file_path:
            return

        try:
            with open(file_path, "wb") as f:
                f.write(self.compressed_data)

            size_kb = len(self.compressed_data) / 1024
            self.status_label.setText(f"Saved: {os.path.basename(file_path)} ({size_kb:.1f} KB)")
            QMessageBox.information(self, "Success", f"Saved!\n\n{file_path}\nSize: {size_kb:.1f} KB")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed: {str(e)}")

    def export_frames_zip(self):
        frames, durations = self.get_export_frames()

        if not frames:
            QMessageBox.critical(self, "Error", "No frames to export!")
            return

        default_name = "frames"
        if self.gif_path:
            default_name = os.path.splitext(os.path.basename(self.gif_path))[0] + "_frames"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Frames as ZIP",
            default_name + ".zip",
            "ZIP files (*.zip)"
        )

        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, 'w') as zf:
                for i, frame in enumerate(frames):
                    buffer = io.BytesIO()
                    frame.save(buffer, format='PNG')
                    zf.writestr(f"frame_{i + 1:04d}.png", buffer.getvalue())

            self.status_label.setText(f"Exported {len(frames)} frames to ZIP")
            QMessageBox.information(self, "Success", f"Exported {len(frames)} frames!\n\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    # -------------------------------------------------------------------------
    # Mask Repair Methods
    # -------------------------------------------------------------------------

    def copy_mask_from_frame(self):
        """Copy alpha channel from another frame to fix the current frame."""
        if not self.processed_frames or not any(self.processed_frames):
            QMessageBox.warning(self, "Warning", "No processed frames available. Run background removal first.")
            return

        if self.processed_frames[self.current_frame_index] is None:
            QMessageBox.warning(self, "Warning", "Current frame has not been processed yet.")
            return

        # Build list of available source frames
        available = []
        for i, pf in enumerate(self.processed_frames):
            if pf is not None and i != self.current_frame_index:
                available.append(i)

        if not available:
            QMessageBox.warning(self, "Warning", "No other processed frames to copy from.")
            return

        # Show dialog to select source frame
        from PyQt5.QtWidgets import QDialog, QListWidget, QDialogButtonBox, QListWidgetItem

        dialog = QDialog(self)
        dialog.setWindowTitle("Copy Mask From Frame")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Select a source frame to copy the mask from:"))

        list_widget = QListWidget()
        for idx in available:
            item = QListWidgetItem(f"Frame {idx + 1}")
            item.setData(Qt.UserRole, idx)
            list_widget.addItem(item)
        list_widget.setCurrentRow(0)
        layout.addWidget(list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            selected = list_widget.currentItem()
            if selected:
                source_idx = selected.data(Qt.UserRole)
                self._apply_mask_from_frame(source_idx)

    def _apply_mask_from_frame(self, source_idx):
        """Apply the alpha channel from source frame to current frame."""
        source = self.processed_frames[source_idx]
        target = self.processed_frames[self.current_frame_index]

        if source.size != target.size:
            source = source.resize(target.size, Image.Resampling.LANCZOS)

        # Get alpha channels
        source_alpha = source.split()[3] if source.mode == "RGBA" else Image.new("L", source.size, 255)

        # Apply source alpha to target
        target_rgb = target.convert("RGB")
        target_rgba = target_rgb.copy()
        target_rgba.putalpha(source_alpha)

        self.processed_frames[self.current_frame_index] = target_rgba
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"Copied mask from frame {source_idx + 1} to frame {self.current_frame_index + 1}")

    def auto_fix_outliers(self):
        """Detect and fix frames where the mask suddenly changes (outliers)."""
        if not self.processed_frames or not any(self.processed_frames):
            QMessageBox.warning(self, "Warning", "No processed frames available. Run background removal first.")
            return

        # Calculate mask area for each frame
        mask_areas = []
        for i, pf in enumerate(self.processed_frames):
            if pf is not None and pf.mode == "RGBA":
                alpha = np.array(pf.split()[3])
                area = np.sum(alpha > 128)
                mask_areas.append((i, area))
            else:
                mask_areas.append((i, None))

        # Find outliers - frames with significant deviation from neighbors
        outliers = []
        valid_areas = [(i, a) for i, a in mask_areas if a is not None]

        if len(valid_areas) < 3:
            QMessageBox.information(self, "Info", "Not enough frames to detect outliers.")
            return

        # Calculate median area
        areas_only = [a for _, a in valid_areas]
        median_area = np.median(areas_only)
        std_area = np.std(areas_only)

        # Detect outliers (more than 2 std from median, or sudden changes)
        for i in range(len(valid_areas)):
            idx, area = valid_areas[i]

            # Check if this frame deviates significantly from median
            if abs(area - median_area) > 2 * std_area:
                outliers.append(idx)
                continue

            # Check sudden change from neighbors
            if i > 0 and i < len(valid_areas) - 1:
                prev_area = valid_areas[i - 1][1]
                next_area = valid_areas[i + 1][1]
                neighbor_avg = (prev_area + next_area) / 2

                # If this frame differs by more than 30% from neighbors but neighbors are similar
                if abs(prev_area - next_area) < median_area * 0.15:  # Neighbors are similar
                    if abs(area - neighbor_avg) > median_area * 0.3:  # This frame is different
                        if idx not in outliers:
                            outliers.append(idx)

        if not outliers:
            QMessageBox.information(self, "Info", "No outlier frames detected!")
            return

        # Ask user to confirm
        reply = QMessageBox.question(
            self, "Fix Outliers",
            f"Found {len(outliers)} potential outlier frames:\n"
            f"Frames: {', '.join(str(o + 1) for o in outliers[:10])}"
            + (f"... and {len(outliers) - 10} more" if len(outliers) > 10 else "") +
            "\n\nFix these by blending from neighboring frames?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            fixed = 0
            for idx in outliers:
                if self._fix_outlier_frame(idx, valid_areas):
                    fixed += 1

            self.show_frame(self.current_frame_index)
            self.status_label.setText(f"Fixed {fixed} outlier frames")

    def _fix_outlier_frame(self, idx, valid_areas):
        """Fix a single outlier frame by interpolating alpha from neighbors."""
        # Find nearest valid neighbors
        prev_idx = None
        next_idx = None

        for i, area in valid_areas:
            if i < idx and i not in [idx]:
                prev_idx = i
            if i > idx and next_idx is None:
                next_idx = i
                break

        if prev_idx is None and next_idx is None:
            return False

        target = self.processed_frames[idx]
        if target is None:
            return False

        # Get neighbor masks
        if prev_idx is not None and next_idx is not None:
            # Blend both neighbors
            prev_alpha = np.array(self.processed_frames[prev_idx].split()[3], dtype=np.float32)
            next_alpha = np.array(self.processed_frames[next_idx].split()[3], dtype=np.float32)

            # Resize if needed
            if prev_alpha.shape != np.array(target.split()[3]).shape:
                prev_alpha = np.array(self.processed_frames[prev_idx].resize(target.size).split()[3], dtype=np.float32)
            if next_alpha.shape != np.array(target.split()[3]).shape:
                next_alpha = np.array(self.processed_frames[next_idx].resize(target.size).split()[3], dtype=np.float32)

            # Interpolate
            t = (idx - prev_idx) / (next_idx - prev_idx)
            new_alpha = ((1 - t) * prev_alpha + t * next_alpha).astype(np.uint8)

        elif prev_idx is not None:
            new_alpha = np.array(self.processed_frames[prev_idx].split()[3])
            if new_alpha.shape != np.array(target.split()[3]).shape:
                new_alpha = np.array(self.processed_frames[prev_idx].resize(target.size).split()[3])
        else:
            new_alpha = np.array(self.processed_frames[next_idx].split()[3])
            if new_alpha.shape != np.array(target.split()[3]).shape:
                new_alpha = np.array(self.processed_frames[next_idx].resize(target.size).split()[3])

        # Apply new alpha
        target_rgb = target.convert("RGB")
        new_frame = target_rgb.copy()
        new_frame.putalpha(Image.fromarray(new_alpha))
        self.processed_frames[idx] = new_frame

        return True

    def toggle_paint_mode(self):
        """Toggle paint mode for restoring deleted foreground areas."""
        if self.btn_paint_mode.isChecked():
            self.paint_mode_active = True
            self.erase_mode_active = False
            self.btn_erase_mode.setChecked(False)
            self.preview_label.setCursor(Qt.CrossCursor)
            self.status_label.setText("Paint Mode: Click and drag to restore foreground")
        else:
            self.paint_mode_active = False
            self.preview_label.setCursor(Qt.ArrowCursor)
            self.status_label.setText("Paint mode disabled")

    def toggle_erase_mode(self):
        """Toggle erase mode for removing background areas."""
        if self.btn_erase_mode.isChecked():
            self.erase_mode_active = True
            self.paint_mode_active = False
            self.btn_paint_mode.setChecked(False)
            self.preview_label.setCursor(Qt.CrossCursor)
            self.status_label.setText("Erase Mode: Click and drag to remove background")
        else:
            self.erase_mode_active = False
            self.preview_label.setCursor(Qt.ArrowCursor)
            self.status_label.setText("Erase mode disabled")

    def _reset_preview_events(self):
        """Reset preview to normal mode."""
        self.preview_label.setCursor(Qt.ArrowCursor)
        self.paint_mode_active = False
        self.erase_mode_active = False
        self.sam2_click_mode = False

    def _get_image_coords(self, event):
        """Convert widget coordinates to image coordinates."""
        if not self.processed_frames or self.processed_frames[self.current_frame_index] is None:
            return None

        frame = self.processed_frames[self.current_frame_index]

        # Get widget and image dimensions
        widget_w = self.preview_label.width()
        widget_h = self.preview_label.height()
        img_w, img_h = frame.size

        # Calculate displayed image size (maintaining aspect ratio)
        preview_width = widget_w - 20
        preview_height = widget_h - 20

        frame_ratio = img_w / img_h
        preview_ratio = preview_width / preview_height

        if frame_ratio > preview_ratio:
            display_w = min(preview_width, img_w)
            display_h = int(display_w / frame_ratio)
        else:
            display_h = min(preview_height, img_h)
            display_w = int(display_h * frame_ratio)

        # Calculate offset (image is centered)
        offset_x = (widget_w - display_w) // 2
        offset_y = (widget_h - display_h) // 2

        # Convert widget coords to image coords
        widget_x = event.x()
        widget_y = event.y()

        img_x = int((widget_x - offset_x) * img_w / display_w)
        img_y = int((widget_y - offset_y) * img_h / display_h)

        # Clamp to image bounds
        img_x = max(0, min(img_w - 1, img_x))
        img_y = max(0, min(img_h - 1, img_y))

        return (img_x, img_y)

    def _paint_mouse_press(self, event):
        """Handle mouse press for painting."""
        if event.button() == Qt.LeftButton:
            coords = self._get_image_coords(event)
            if coords:
                self.last_paint_pos = coords
                self._paint_at(coords)

    def _paint_mouse_move(self, event):
        """Handle mouse move for painting."""
        if event.buttons() & Qt.LeftButton:
            coords = self._get_image_coords(event)
            if coords and self.last_paint_pos:
                self._paint_line(self.last_paint_pos, coords)
                self.last_paint_pos = coords

    def _paint_mouse_release(self, event):
        """Handle mouse release for painting."""
        self.last_paint_pos = None
        self.show_frame(self.current_frame_index)

    def _paint_at(self, pos):
        """Paint at a single position."""
        if self.processed_frames[self.current_frame_index] is None:
            return

        frame = self.processed_frames[self.current_frame_index]
        if frame.mode != "RGBA":
            frame = frame.convert("RGBA")

        alpha = frame.split()[3]
        draw = ImageDraw.Draw(alpha)

        brush_size = self.brush_size_spin.value()

        if self.paint_mode_active:
            # Paint white (full opacity) to restore foreground
            draw.ellipse(
                [pos[0] - brush_size, pos[1] - brush_size,
                 pos[0] + brush_size, pos[1] + brush_size],
                fill=255
            )
        elif self.erase_mode_active:
            # Paint black (transparent) to erase
            draw.ellipse(
                [pos[0] - brush_size, pos[1] - brush_size,
                 pos[0] + brush_size, pos[1] + brush_size],
                fill=0
            )

        frame.putalpha(alpha)
        self.processed_frames[self.current_frame_index] = frame

    def _paint_line(self, start, end):
        """Paint a line from start to end position."""
        if self.processed_frames[self.current_frame_index] is None:
            return

        frame = self.processed_frames[self.current_frame_index]
        if frame.mode != "RGBA":
            frame = frame.convert("RGBA")

        alpha = frame.split()[3]
        draw = ImageDraw.Draw(alpha)

        brush_size = self.brush_size_spin.value()
        fill_value = 255 if self.paint_mode_active else 0

        # Draw line with circles
        draw.line([start, end], fill=fill_value, width=brush_size * 2)
        draw.ellipse(
            [end[0] - brush_size, end[1] - brush_size,
             end[0] + brush_size, end[1] + brush_size],
            fill=fill_value
        )

        frame.putalpha(alpha)
        self.processed_frames[self.current_frame_index] = frame
        self.show_frame(self.current_frame_index)

    def sam_click_fix(self):
        """Use SAM (Segment Anything Model) for click-to-segment."""
        # Check if SAM is available
        try:
            from segment_anything import sam_model_registry, SamPredictor
            sam_available = True
        except ImportError:
            sam_available = False

        if not sam_available:
            reply = QMessageBox.question(
                self, "SAM Not Installed",
                "Segment Anything Model (SAM) is not installed.\n\n"
                "Would you like to install it? (This may take a few minutes)\n\n"
                "Note: SAM requires ~2.5GB of model weights to be downloaded.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self._install_sam()
            return

        if not self.original_frames:
            QMessageBox.warning(self, "Warning", "Load a GIF first!")
            return

        # Enable SAM click mode
        self.status_label.setText("SAM Mode: Click on the subject to segment it")
        self.preview_label.setCursor(Qt.CrossCursor)
        self.preview_label.mousePressEvent = self._sam_click

    def _install_sam(self):
        """Install SAM package."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Installing SAM...")
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # Indeterminate

        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "segment-anything"],
                capture_output=True,
                text=True
            )

            self.progress_bar.setVisible(False)

            if result.returncode == 0:
                QMessageBox.information(
                    self, "Success",
                    "SAM package installed!\n\n"
                    "Note: You still need to download SAM model weights.\n"
                    "Visit: https://github.com/facebookresearch/segment-anything\n\n"
                    "Download 'sam_vit_h_4b8939.pth' and place it in the app folder."
                )
            else:
                QMessageBox.critical(self, "Error", f"Installation failed:\n{result.stderr}")

        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"Installation failed: {str(e)}")

    def _sam_click(self, event):
        """Handle click for SAM segmentation."""
        if event.button() != Qt.LeftButton:
            return

        coords = self._get_image_coords(event)
        if not coords:
            return

        try:
            from segment_anything import sam_model_registry, SamPredictor

            # Look for SAM model
            model_path = None
            for name in ["sam_vit_h_4b8939.pth", "sam_vit_l_0b3195.pth", "sam_vit_b_01ec64.pth"]:
                path = os.path.join(get_app_dir(), name)
                if os.path.exists(path):
                    model_path = path
                    model_type = name.split("_")[2]  # h, l, or b
                    break

            if not model_path:
                QMessageBox.warning(
                    self, "SAM Model Not Found",
                    "SAM model weights not found.\n\n"
                    "Download from: https://github.com/facebookresearch/segment-anything\n"
                    "Place the .pth file in the app folder."
                )
                self._reset_preview_events()
                self.preview_label.setCursor(Qt.ArrowCursor)
                return

            self.status_label.setText("Running SAM segmentation...")
            QApplication.processEvents()

            # Load model
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"

            model_type_map = {"h": "vit_h", "l": "vit_l", "b": "vit_b"}
            sam = sam_model_registry[model_type_map[model_type]](checkpoint=model_path)
            sam.to(device)
            predictor = SamPredictor(sam)

            # Get current frame
            frame = self.original_frames[self.current_frame_index]
            img_array = np.array(frame.convert("RGB"))

            predictor.set_image(img_array)

            # Get mask from click
            input_point = np.array([[coords[0], coords[1]]])
            input_label = np.array([1])  # 1 = foreground

            masks, scores, _ = predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True
            )

            # Use the best mask
            best_idx = np.argmax(scores)
            mask = masks[best_idx]

            # Apply mask to frame
            alpha = (mask * 255).astype(np.uint8)
            frame_rgb = frame.convert("RGB")
            result = frame_rgb.copy()
            result.putalpha(Image.fromarray(alpha))

            self.processed_frames[self.current_frame_index] = result
            self.show_processed = True
            self.show_frame(self.current_frame_index)

            self.status_label.setText(f"SAM segmentation complete (score: {scores[best_idx]:.2f})")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"SAM segmentation failed:\n{str(e)}")

        # Reset to normal mode
        self._reset_preview_events()
        self.preview_label.setCursor(Qt.ArrowCursor)

    # -------------------------------------------------------------------------
    # SAM 2 Video Segmentation Methods
    # -------------------------------------------------------------------------

    def start_sam2_click_mode(self):
        """Enter SAM 2 click mode - user clicks on subject to segment."""
        # Check if SAM 2 checkpoint exists
        checkpoint_found = False
        checkpoints = [
            "sam2.1_hiera_large.pt", "sam2.1_hiera_base_plus.pt",
            "sam2.1_hiera_small.pt", "sam2.1_hiera_tiny.pt",
            "sam2_hiera_large.pt", "sam2_hiera_base_plus.pt",
            "sam2_hiera_small.pt", "sam2_hiera_tiny.pt",
        ]

        for ckpt in checkpoints:
            if os.path.exists(os.path.join(get_app_dir(), ckpt)):
                checkpoint_found = True
                break
            if os.path.exists(os.path.join(get_app_dir(), "checkpoints", ckpt)):
                checkpoint_found = True
                break

        if not checkpoint_found:
            reply = QMessageBox.question(
                self, "SAM 2 Checkpoint Not Found",
                "SAM 2 model checkpoint not found.\n\n"
                "Would you like to download it automatically?\n\n"
                "Options:\n"
                "• Yes = Download sam2.1_hiera_large.pt (~900MB, best quality)\n"
                "• No = Download sam2.1_hiera_tiny.pt (~150MB, faster)\n"
                "• Cancel = Don't download",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self._download_sam2_checkpoint("large")
                return
            elif reply == QMessageBox.No:
                self._download_sam2_checkpoint("tiny")
                return
            else:
                return

        # Enter click mode
        self.sam2_click_mode = True
        self.sam2_click_points = []
        self.sam2_click_labels = []

        self.preview_label.setCursor(Qt.CrossCursor)

        self.status_label.setText(
            "SAM 2: Left-click on SUBJECT (foreground), Right-click on BACKGROUND. "
            "Press Enter when done, Esc to cancel."
        )
        self.btn_remove_bg.setText("✓ Done Clicking (Enter)")
        self.btn_remove_bg.clicked.disconnect()
        self.btn_remove_bg.clicked.connect(self.finish_sam2_clicks)

    def _download_sam2_checkpoint(self, size="large"):
        """Download SAM 2 checkpoint file."""
        # SAM 2.1 checkpoint URLs from Facebook
        checkpoints = {
            "large": (
                "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt",
                "sam2.1_hiera_large.pt",
                897  # MB
            ),
            "base_plus": (
                "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt",
                "sam2.1_hiera_base_plus.pt",
                321
            ),
            "small": (
                "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt",
                "sam2.1_hiera_small.pt",
                184
            ),
            "tiny": (
                "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt",
                "sam2.1_hiera_tiny.pt",
                155
            ),
        }

        url, filename, size_mb = checkpoints.get(size, checkpoints["large"])
        output_path = os.path.join(get_app_dir(), filename)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFormat(f"Downloading {filename} (0%)")
        self.status_label.setText(f"Downloading SAM 2 checkpoint ({size_mb}MB)...")
        QApplication.processEvents()

        try:
            import urllib.request

            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, int(block_num * block_size * 100 / total_size))
                    downloaded_mb = block_num * block_size / (1024 * 1024)
                    self.progress_bar.setValue(percent)
                    self.progress_bar.setFormat(
                        f"Downloading {filename} ({percent}% - {downloaded_mb:.0f}MB)"
                    )
                    QApplication.processEvents()

            urllib.request.urlretrieve(url, output_path, progress_hook)

            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Downloaded {filename} successfully!")

            QMessageBox.information(
                self, "Download Complete",
                f"SAM 2 checkpoint downloaded!\n\n"
                f"File: {filename}\n"
                f"Size: {size_mb}MB\n\n"
                "Click 'Remove Background' again to start."
            )

        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(
                self, "Download Failed",
                f"Failed to download SAM 2 checkpoint:\n\n{str(e)}\n\n"
                "You can manually download from:\n"
                "https://github.com/facebookresearch/sam2#download-checkpoints"
            )
            self.status_label.setText("Download failed")

    def _sam2_click_handler(self, event):
        """Handle mouse clicks for SAM 2 point selection."""
        if not self.sam2_click_mode:
            return

        coords = self._get_image_coords_original(event)
        if not coords:
            return

        if event.button() == Qt.LeftButton:
            # Foreground point
            self.sam2_click_points.append(coords)
            self.sam2_click_labels.append(1)
            self.status_label.setText(
                f"SAM 2: Added foreground point ({len(self.sam2_click_points)} points). "
                "Left=foreground, Right=background, Enter=process"
            )
        elif event.button() == Qt.RightButton:
            # Background point
            self.sam2_click_points.append(coords)
            self.sam2_click_labels.append(0)
            self.status_label.setText(
                f"SAM 2: Added background point ({len(self.sam2_click_points)} points). "
                "Left=foreground, Right=background, Enter=process"
            )

        # Redraw preview with click markers
        self._draw_sam2_click_markers()

    def _get_image_coords_original(self, event):
        """Convert widget coordinates to original image coordinates."""
        if not self.original_frames:
            return None

        frame = self.original_frames[self.current_frame_index]

        # Get widget and image dimensions
        widget_w = self.preview_label.width()
        widget_h = self.preview_label.height()
        img_w, img_h = frame.size

        # Calculate displayed image size (maintaining aspect ratio)
        preview_width = widget_w - 20
        preview_height = widget_h - 20

        frame_ratio = img_w / img_h
        preview_ratio = preview_width / preview_height

        if frame_ratio > preview_ratio:
            display_w = min(preview_width, img_w)
            display_h = int(display_w / frame_ratio)
        else:
            display_h = min(preview_height, img_h)
            display_w = int(display_h * frame_ratio)

        # Calculate offset (image is centered)
        offset_x = (widget_w - display_w) // 2
        offset_y = (widget_h - display_h) // 2

        # Convert widget coords to image coords
        widget_x = event.x()
        widget_y = event.y()

        img_x = int((widget_x - offset_x) * img_w / display_w)
        img_y = int((widget_y - offset_y) * img_h / display_h)

        # Check bounds
        if img_x < 0 or img_x >= img_w or img_y < 0 or img_y >= img_h:
            return None

        return (img_x, img_y)

    def _draw_sam2_click_markers(self):
        """Draw click point markers on the preview."""
        if not self.original_frames:
            return

        frame = self.original_frames[self.current_frame_index].copy()

        # Draw markers on frame
        draw = ImageDraw.Draw(frame)
        for i, (point, label) in enumerate(zip(self.sam2_click_points, self.sam2_click_labels)):
            x, y = point
            color = (0, 255, 0, 255) if label == 1 else (255, 0, 0, 255)  # Green=fg, Red=bg
            r = 8
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=(255, 255, 255, 255))

        # Update preview
        self._show_frame_with_image(frame)

    def _show_frame_with_image(self, frame):
        """Display a PIL image in the preview label."""
        preview_width = self.preview_label.width() - 20
        preview_height = self.preview_label.height() - 20

        if preview_width <= 0:
            preview_width = 640
        if preview_height <= 0:
            preview_height = 480

        frame_ratio = frame.width / frame.height
        preview_ratio = preview_width / preview_height

        if frame_ratio > preview_ratio:
            new_width = min(preview_width, frame.width)
            new_height = int(new_width / frame_ratio)
        else:
            new_height = min(preview_height, frame.height)
            new_width = int(new_height * frame_ratio)

        display_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if self.preview_bg_color is None:
            bg = create_checkerboard(new_width, new_height)
        else:
            bg = create_solid_background(new_width, new_height, self.preview_bg_color)

        if display_frame.mode == "RGBA":
            bg.paste(display_frame, mask=display_frame.split()[3])
        else:
            bg.paste(display_frame)

        pixmap = pil_to_qpixmap(bg.convert("RGBA"))
        self.preview_label.setPixmap(pixmap)

    def finish_sam2_clicks(self):
        """Process all frames with SAM 2 using the clicked points."""
        if not self.sam2_click_points:
            QMessageBox.warning(self, "Warning", "Please click at least one point on the subject.")
            return

        self.cancel_sam2_click_mode()
        self.run_sam2_processing()

    def cancel_sam2_click_mode(self):
        """Exit SAM 2 click mode without processing."""
        self.sam2_click_mode = False
        self.preview_label.setCursor(Qt.ArrowCursor)
        self._reset_preview_events()

        self.btn_remove_bg.setText("🎨 Remove Background")
        self.btn_remove_bg.clicked.disconnect()
        self.btn_remove_bg.clicked.connect(self.remove_backgrounds)

        self.show_frame(self.current_frame_index)

    # -------------------------------------------------------------------------
    # Color Key Methods
    # -------------------------------------------------------------------------

    def pick_colorkey_color(self):
        """Open color picker for background color selection."""
        color = QColorDialog.getColor(
            QColor(*self.colorkey_color), self, "Select Background Color"
        )
        if color.isValid():
            self.colorkey_color = (color.red(), color.green(), color.blue())
            self.colorkey_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 2px solid #3a3a5a;"
            )

    def auto_detect_bg_color(self):
        """Auto-detect background color from frame corners."""
        if not self.original_frames:
            QMessageBox.warning(self, "Warning", "Load a GIF first!")
            return

        frame = self.original_frames[self.current_frame_index]
        img = frame.convert("RGB")
        pixels = img.load()
        w, h = img.size

        # Sample corners and edges
        samples = []
        # Corners
        for x, y in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]:
            samples.append(pixels[x, y])
        # Edge midpoints
        for x, y in [(w//2, 0), (w//2, h-1), (0, h//2), (w-1, h//2)]:
            samples.append(pixels[x, y])

        # Find most common color (simple mode)
        from collections import Counter
        color_counts = Counter(samples)
        most_common = color_counts.most_common(1)[0][0]

        self.colorkey_color = most_common
        self.colorkey_color_btn.setStyleSheet(
            f"background-color: rgb{most_common}; border: 2px solid #3a3a5a;"
        )
        self.status_label.setText(f"Detected background color: RGB{most_common}")

    def run_colorkey_removal(self):
        """Remove background using color keying (flood fill from edges)."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.original_frames))

        bg_color = self.colorkey_color
        threshold = self.colorkey_threshold.value() / 100.0 * 255  # Convert to 0-255
        outer_only = self.colorkey_outer_only.isChecked()
        ai_refine = self.colorkey_ai_refine.isChecked()
        ai_protect = self.colorkey_ai_protect.isChecked()

        # Start rembg worker if AI features enabled
        rembg_proc = None
        temp_dir = None
        if ai_refine or ai_protect:
            self.progress_bar.setFormat("Starting AI...")
            QApplication.processEvents()

            temp_dir = tempfile.mkdtemp(prefix='colorkey_ai_')
            rembg_script = os.path.join(get_app_dir(), "rembg_only_worker.py")
            rembg_proc = subprocess.Popen(
                [sys.executable, rembg_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            ready = rembg_proc.stdout.readline().strip()
            if ready != "READY":
                QMessageBox.warning(self, "Warning", f"AI failed to start: {ready}")
                ai_refine = False
                ai_protect = False

        try:
            for i, frame in enumerate(self.original_frames):
                if i in self.deleted_frames:
                    self.processed_frames[i] = None
                    continue

                self.progress_bar.setFormat(f"Frame {i+1}/{len(self.original_frames)}...")
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()

                # Get AI protection mask if enabled
                protect_mask = None
                if ai_protect and rembg_proc:
                    protect_mask = self._get_ai_mask(frame, rembg_proc, temp_dir, i)

                # Color key removal (with optional protection mask)
                result = self._colorkey_frame(frame, bg_color, threshold, outer_only, protect_mask)

                # AI edge refinement (if enabled)
                if ai_refine and rembg_proc:
                    result = self._refine_edges_with_ai(result, frame, rembg_proc, temp_dir, i)

                self.processed_frames[i] = result

        finally:
            # Cleanup
            if rembg_proc:
                try:
                    rembg_proc.stdin.write("QUIT\n")
                    rembg_proc.stdin.flush()
                    rembg_proc.terminate()
                except:
                    pass
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)

        self.progress_bar.setVisible(False)
        self.show_processed = True
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"Color key removal complete! ({len(self.original_frames)} frames)")

    def _get_ai_mask(self, frame, rembg_proc, temp_dir, frame_idx):
        """Get AI mask from rembg for subject protection."""
        import numpy as np

        # Save frame for rembg
        input_path = os.path.join(temp_dir, f"protect_input_{frame_idx}.png")
        output_path = os.path.join(temp_dir, f"protect_output_{frame_idx}.png")
        frame.save(input_path, "PNG")

        # Run rembg
        cmd = json.dumps({"input": input_path, "output": output_path})
        rembg_proc.stdin.write(cmd + "\n")
        rembg_proc.stdin.flush()
        result = rembg_proc.stdout.readline().strip()

        if result != "OK" or not os.path.exists(output_path):
            return None  # No protection if AI fails

        # Load AI result and extract alpha as mask
        ai_result = Image.open(output_path).convert("RGBA")
        ai_mask = np.array(ai_result.split()[3])  # Alpha channel

        return ai_mask

    def _colorkey_frame(self, frame, bg_color, threshold, outer_only, protect_mask=None):
        """Apply color key removal to a single frame.

        Args:
            protect_mask: Optional numpy array where non-zero pixels are protected from removal
        """
        img = frame.convert("RGBA")
        pixels = img.load()
        w, h = img.size

        # Create mask (255 = keep, 0 = remove)
        mask = Image.new("L", (w, h), 255)
        mask_pixels = mask.load()

        # Load protection mask if provided
        protect_pixels = None
        if protect_mask is not None:
            protect_img = Image.fromarray(protect_mask).resize((w, h), Image.Resampling.NEAREST)
            protect_pixels = protect_img.load()

        def color_match(pixel, target, thresh):
            """Check if pixel color matches target within threshold."""
            r_diff = abs(pixel[0] - target[0])
            g_diff = abs(pixel[1] - target[1])
            b_diff = abs(pixel[2] - target[2])
            return (r_diff + g_diff + b_diff) / 3 <= thresh

        def is_protected(x, y):
            """Check if pixel is protected by AI mask."""
            if protect_pixels is None:
                return False
            return protect_pixels[x, y] > 128  # Protected if AI says it's foreground

        if outer_only:
            # Flood fill from edges
            from collections import deque
            visited = set()
            queue = deque()

            # Add all edge pixels to queue
            for x in range(w):
                queue.append((x, 0))
                queue.append((x, h - 1))
            for y in range(h):
                queue.append((0, y))
                queue.append((w - 1, y))

            while queue:
                x, y = queue.popleft()
                if (x, y) in visited:
                    continue
                if x < 0 or x >= w or y < 0 or y >= h:
                    continue

                visited.add((x, y))

                # Skip if this pixel is protected by AI
                if is_protected(x, y):
                    continue

                pixel = pixels[x, y]

                if color_match(pixel, bg_color, threshold):
                    mask_pixels[x, y] = 0  # Mark for removal
                    # Add neighbors
                    queue.append((x + 1, y))
                    queue.append((x - 1, y))
                    queue.append((x, y + 1))
                    queue.append((x, y - 1))
        else:
            # Remove all matching pixels regardless of position
            for y in range(h):
                for x in range(w):
                    # Skip if protected
                    if is_protected(x, y):
                        continue
                    pixel = pixels[x, y]
                    if color_match(pixel, bg_color, threshold):
                        mask_pixels[x, y] = 0

        # Apply mask as alpha channel
        img.putalpha(mask)
        return img

    def _refine_edges_with_ai(self, colorkey_result, original_frame, rembg_proc, temp_dir, frame_idx):
        """Refine edges of color key result using AI (rembg)."""
        # Save original frame for rembg
        input_path = os.path.join(temp_dir, f"input_{frame_idx}.png")
        output_path = os.path.join(temp_dir, f"output_{frame_idx}.png")
        original_frame.save(input_path, "PNG")

        # Run rembg
        cmd = json.dumps({"input": input_path, "output": output_path})
        rembg_proc.stdin.write(cmd + "\n")
        rembg_proc.stdin.flush()
        result = rembg_proc.stdout.readline().strip()

        if result != "OK" or not os.path.exists(output_path):
            return colorkey_result  # Fall back to color key only

        # Load AI result
        ai_result = Image.open(output_path).convert("RGBA")

        # Get masks
        colorkey_mask = np.array(colorkey_result.split()[3])
        ai_mask = np.array(ai_result.split()[3])

        # Find edge region (where color key mask transitions)
        # Dilate and erode to find edge band
        from PIL import ImageFilter

        ck_mask_img = Image.fromarray(colorkey_mask)

        # Create edge band: dilate - erode gives us the edge region
        dilated = ck_mask_img.filter(ImageFilter.MaxFilter(7))
        eroded = ck_mask_img.filter(ImageFilter.MinFilter(7))

        dilated_arr = np.array(dilated)
        eroded_arr = np.array(eroded)

        # Edge region is where dilated != eroded
        edge_region = (dilated_arr != eroded_arr)

        # Create refined mask: use AI mask for edges, color key for interior
        refined_mask = colorkey_mask.copy()
        refined_mask[edge_region] = ai_mask[edge_region]

        # Apply refined mask
        result_img = original_frame.convert("RGBA")
        result_img.putalpha(Image.fromarray(refined_mask))

        # Cleanup temp files
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass

        return result_img

    def run_auto_sam2_hybrid(self):
        """Run Auto + SAM 2 hybrid: rembg detects subject, SAM 2 propagates."""
        # Check for SAM 2 checkpoint first
        checkpoint_found = False
        checkpoints = [
            "sam2.1_hiera_large.pt", "sam2.1_hiera_base_plus.pt",
            "sam2.1_hiera_small.pt", "sam2.1_hiera_tiny.pt",
            "sam2_hiera_large.pt", "sam2_hiera_base_plus.pt",
            "sam2_hiera_small.pt", "sam2_hiera_tiny.pt",
        ]

        for ckpt in checkpoints:
            if os.path.exists(os.path.join(get_app_dir(), ckpt)):
                checkpoint_found = True
                break
            if os.path.exists(os.path.join(get_app_dir(), "checkpoints", ckpt)):
                checkpoint_found = True
                break

        if not checkpoint_found:
            reply = QMessageBox.question(
                self, "SAM 2 Checkpoint Not Found",
                "SAM 2 model checkpoint not found.\n\n"
                "Would you like to download it automatically?\n\n"
                "Options:\n"
                "• Yes = Download sam2.1_hiera_large.pt (~900MB, best quality)\n"
                "• No = Download sam2.1_hiera_tiny.pt (~150MB, faster)\n"
                "• Cancel = Don't download",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self._download_sam2_checkpoint("large")
            elif reply == QMessageBox.No:
                self._download_sam2_checkpoint("tiny")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setFormat("Starting Auto + SAM 2...")

        self.auto_sam2_thread = AutoSAM2Thread(
            self.original_frames,
            self.deleted_frames
        )
        self.auto_sam2_thread.progress.connect(self.on_sam2_progress)
        self.auto_sam2_thread.frame_done.connect(self.on_frame_processed)
        self.auto_sam2_thread.finished_all.connect(self.on_sam2_complete)
        self.auto_sam2_thread.error_occurred.connect(self.on_sam2_error)
        self.auto_sam2_thread.start()

    def run_sam2_processing(self):
        """Run SAM 2 video segmentation on all frames in background thread."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setFormat("Starting SAM 2...")

        self.sam2_thread = SAM2Thread(
            self.original_frames,
            self.deleted_frames,
            self.sam2_click_points,
            self.sam2_click_labels,
            self.current_frame_index
        )
        self.sam2_thread.progress.connect(self.on_sam2_progress)
        self.sam2_thread.frame_done.connect(self.on_frame_processed)
        self.sam2_thread.finished_all.connect(self.on_sam2_complete)
        self.sam2_thread.error_occurred.connect(self.on_sam2_error)
        self.sam2_thread.start()

    def on_sam2_progress(self, status):
        """Handle SAM 2 progress updates."""
        self.progress_bar.setFormat(status)
        self.status_label.setText(status)

    def on_sam2_complete(self, num_frames):
        """Handle SAM 2 completion."""
        self.progress_bar.setVisible(False)
        self.show_processed = True
        self.show_frame(self.current_frame_index)
        self.status_label.setText(f"SAM 2 complete! Segmented {num_frames} frames.")

    def on_sam2_error(self, error_msg):
        """Handle SAM 2 error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "SAM 2 Error", f"SAM 2 processing failed:\n\n{error_msg}")
        self.status_label.setText("SAM 2 failed - try RVM or rembg instead")

    def eventFilter(self, obj, event):
        """Handle mouse events on preview label."""
        if obj == self.preview_label and event.type() == QEvent.MouseButtonPress:
            if self.sam2_click_mode:
                self._sam2_click_handler(event)
                return True
            elif self.paint_mode_active or self.erase_mode_active:
                self._paint_mouse_press(event)
                return True
        elif obj == self.preview_label and event.type() == QEvent.MouseMove:
            if self.paint_mode_active or self.erase_mode_active:
                self._paint_mouse_move(event)
                return True
        elif obj == self.preview_label and event.type() == QEvent.MouseButtonRelease:
            if self.paint_mode_active or self.erase_mode_active:
                self._paint_mouse_release(event)
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        # Handle SAM 2 click mode keys
        if self.sam2_click_mode:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.finish_sam2_clicks()
                return
            elif event.key() == Qt.Key_Escape:
                self.cancel_sam2_click_mode()
                self.status_label.setText("SAM 2 cancelled")
                return

        # Normal key handling
        if event.key() == Qt.Key_Left:
            self.prev_frame()
        elif event.key() == Qt.Key_Right:
            self.next_frame()
        elif event.key() == Qt.Key_Delete:
            self.delete_current_frame()
        elif event.key() == Qt.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key_Home:
            self.show_frame(0)
        elif event.key() == Qt.Key_End:
            if self.original_frames:
                self.show_frame(len(self.original_frames) - 1)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    window = GifBackgroundRemover()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
