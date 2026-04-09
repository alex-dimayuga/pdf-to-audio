import subprocess
import sys
import shutil
import urllib.request
import zipfile
import tarfile
import platform
import ssl
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def download_file(url, destination):
    """Download a file with a progress bar, following redirects and bypassing SSL issues."""
    from tqdm import tqdm

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    urllib.request.install_opener(opener)

    with opener.open(url) as response:
        total = int(response.headers.get("Content-Length", 0))
        filename = Path(destination).name

        with open(destination, "wb") as f, tqdm(
            desc=f"    {filename}",
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            ncols=70,
        ) as bar:
            chunk_size = 8192
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                bar.update(len(chunk))


def apt_install(package):
    """Run apt update then install a package with sudo."""
    print(f"  Running apt update...")
    subprocess.run(["sudo", "apt-get", "update", "-y"], capture_output=True)
    result = subprocess.run(["sudo", "apt-get", "install", "-y", package])
    return result.returncode == 0


def ensure_homebrew():
    """Installs Homebrew if not present on Mac."""
    if shutil.which("brew"):
        print("  ✔ Homebrew already installed")
        return True

    print("  ✘ Homebrew not found — installing...")
    print("    (This may take a few minutes and may ask for your password...)")
    try:
        install_script_url = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        install_script = opener.open(install_script_url).read().decode()
        subprocess.run(["/bin/bash", "-c", install_script], check=True)
        print("  ✔ Homebrew installed")
        return True
    except Exception as e:
        print(f"  ✘ Homebrew install failed: {e}")
        print("    Install manually: https://brew.sh")
        input("\nPress Enter to continue anyway or close to exit...")
        return False


def brew_install(package):
    """Installs a package via Homebrew."""
    print(f"  Installing {package} via Homebrew...")
    try:
        subprocess.run(["brew", "install", package], check=True)
        print(f"  ✔ {package} installed")
        return True
    except Exception as e:
        print(f"  ✘ brew install {package} failed: {e}")
        return False


def get_poppler_path():
    global POPPLER_PATH
    system = platform.system()
    poppler_dir = SCRIPT_DIR / "poppler"
    exe_name = "pdftoppm.exe" if system == "Windows" else "pdftoppm"

    # Mac — use Homebrew
    if system == "Darwin":
        if shutil.which("pdftoppm"):
            print("  ✔ Poppler (system)")
            POPPLER_PATH = None
            return
        print("  ✘ Poppler not found — installing via Homebrew...")
        if ensure_homebrew():
            if brew_install("poppler"):
                print("  ✔ Poppler ready")
                POPPLER_PATH = None
        return

    # Linux — use apt
    if system == "Linux":
        if shutil.which("pdftoppm"):
            print("  ✔ Poppler (system)")
            POPPLER_PATH = None
            return
        print("  ✘ Poppler not found — installing via apt...")
        if apt_install("poppler-utils"):
            print("  ✔ Poppler ready")
            POPPLER_PATH = None
        else:
            print("  ✘ apt install failed — try: sudo apt install poppler-utils")
        return

    # Windows — bundle locally
    existing = list(poppler_dir.rglob(exe_name))
    if existing:
        POPPLER_PATH = str(existing[0].parent)
        print(f"  ✔ Poppler (bundled)")
        return

    print("  ✘ Poppler not found — downloading...")
    poppler_dir.mkdir(exist_ok=True)

    try:
        url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v25.07.0-0/Release-25.07.0-0.zip"
        archive_path = SCRIPT_DIR / "poppler.zip"
        download_file(url, archive_path)
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(poppler_dir)
        archive_path.unlink()

        candidates = list(poppler_dir.rglob(exe_name))
        if not candidates:
            raise FileNotFoundError("pdftoppm.exe not found after extraction")
        POPPLER_PATH = str(candidates[0].parent)
        print(f"  ✔ Poppler ready")

    except Exception as e:
        print(f"  ✘ Poppler setup failed: {e}")
        input("\nPress Enter to continue anyway or close to exit...")


def get_ffmpeg_path():
    global FFMPEG_PATH
    system = platform.system()

    if shutil.which("ffmpeg"):
        print("  ✔ FFmpeg (system)")
        FFMPEG_PATH = "ffmpeg"
        return

    # Mac — use Homebrew
    if system == "Darwin":
        print("  ✘ FFmpeg not found — installing via Homebrew...")
        if ensure_homebrew():
            if brew_install("ffmpeg"):
                FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"
        return

    # Linux — use apt
    if system == "Linux":
        print("  ✘ FFmpeg not found — installing via apt...")
        if apt_install("ffmpeg"):
            print("  ✔ FFmpeg ready")
            FFMPEG_PATH = "ffmpeg"
        else:
            print("  ✘ apt install failed — try: sudo apt install ffmpeg")
        return

    # Windows — bundle locally
    ffmpeg_dir = SCRIPT_DIR / "ffmpeg"
    exe_name = "ffmpeg.exe"
    existing = list(ffmpeg_dir.rglob(exe_name))
    if existing:
        FFMPEG_PATH = str(existing[0])
        print(f"  ✔ FFmpeg (bundled)")
        return

    print("  ✘ FFmpeg not found — downloading...")
    ffmpeg_dir.mkdir(exist_ok=True)

    try:
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        archive_path = SCRIPT_DIR / "ffmpeg.zip"
        print("    (This may take a moment, FFmpeg is ~70MB...)")
        download_file(url, archive_path)
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(ffmpeg_dir)
        archive_path.unlink()

        candidates = list(ffmpeg_dir.rglob(exe_name))
        if not candidates:
            raise FileNotFoundError("ffmpeg.exe not found after extraction")
        FFMPEG_PATH = str(candidates[0])
        print(f"  ✔ FFmpeg ready")

    except Exception as e:
        print(f"  ✘ FFmpeg setup failed: {e}")
        input("\nPress Enter to continue anyway or close to exit...")


def get_tesseract_path():
    global TESSERACT_PATH
    system = platform.system()

    if shutil.which("tesseract"):
        print("  ✔ Tesseract (system)")
        TESSERACT_PATH = "tesseract"
        return

    # Mac — use Homebrew
    if system == "Darwin":
        print("  ✘ Tesseract not found — installing via Homebrew...")
        if ensure_homebrew():
            if brew_install("tesseract"):
                TESSERACT_PATH = shutil.which("tesseract") or "tesseract"
        return

    # Linux — use apt
    if system == "Linux":
        print("  ✘ Tesseract not found — installing via apt...")
        if apt_install("tesseract-ocr"):
            print("  ✔ Tesseract ready")
            TESSERACT_PATH = "tesseract"
        else:
            print("  ✘ apt install failed — try: sudo apt install tesseract-ocr")
        return

    # Windows — bundle locally
    tesseract_dir = SCRIPT_DIR / "tesseract"
    exe_name = "tesseract.exe"
    existing = list(tesseract_dir.rglob(exe_name))
    if existing:
        TESSERACT_PATH = str(existing[0])
        print(f"  ✔ Tesseract (bundled)")
        return

    print("  ✘ Tesseract not found — downloading...")
    tesseract_dir.mkdir(exist_ok=True)

    try:
        url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
        installer_path = SCRIPT_DIR / "tesseract_installer.exe"
        print("    (Downloading Tesseract installer...)")
        download_file(url, installer_path)
        subprocess.run([
            str(installer_path),
            "/S",
            f"/D={tesseract_dir.resolve()}"
        ], check=True)
        installer_path.unlink()

        candidates = list(tesseract_dir.rglob(exe_name))
        if not candidates:
            raise FileNotFoundError("tesseract.exe not found after extraction")
        TESSERACT_PATH = str(candidates[0])
        print(f"  ✔ Tesseract ready")

    except Exception as e:
        print(f"  ✘ Tesseract setup failed: {e}")
        input("\nPress Enter to continue anyway or close to exit...")


def check_and_install():
    # ── INSTALL TQDM FIRST so download_file() can use it ──────────
    try:
        __import__("tqdm")
    except ImportError:
        print("Installing tqdm for progress bars...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])

    # ── PIP PACKAGES ──────────────────────────────────────────────
    pip_packages = {
        "pytesseract":  "pytesseract",
        "pdf2image":    "pdf2image",
        "piper":        "piper-tts",
        "fitz":         "pymupdf",
        "docx":         "python-docx",
        "tqdm":         "tqdm",
        "tkinterdnd2":  "tkinterdnd2",
    }

    print("Checking Python packages...")
    for import_name, pip_name in pip_packages.items():
        try:
            __import__(import_name)
            print(f"  ✔ {import_name}")
        except ImportError:
            print(f"  ✘ {import_name} not found — installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"  ✔ {import_name} installed")

    # ── SYSTEM BINARIES ───────────────────────────────────────────
    print("\nChecking Poppler...")
    get_poppler_path()

    print("\nChecking FFmpeg...")
    get_ffmpeg_path()

    print("\nChecking Tesseract...")
    get_tesseract_path()

    # ── TELL PYTESSERACT WHERE TESSERACT IS ───────────────────────
    if TESSERACT_PATH and TESSERACT_PATH != "tesseract":
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # ── PIPER VOICE MODEL FILES ────────────────────────────────────
    print("\nChecking Piper voice model files...")
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high"
    model_files = {
        "en_GB-cori-high.onnx":      f"{base_url}/en_GB-cori-high.onnx",
        "en_GB-cori-high.onnx.json": f"{base_url}/en_GB-cori-high.onnx.json",
    }

    for filename, url in model_files.items():
        filepath = SCRIPT_DIR / filename
        if filepath.exists():
            print(f"  ✔ {filename}")
        else:
            print(f"  ✘ {filename} — downloading...")
            try:
                download_file(url, filepath)
                print(f"  ✔ {filename} downloaded")
            except Exception as e:
                print(f"  ✘ Download failed: {e}")
                input("\nPress Enter to continue anyway or close to exit...")

    print("\nAll checks done. Starting app...\n")


# ── RUN CHECKS BEFORE ANYTHING ELSE ──────────────────────────────
check_and_install()

# ── YOUR NORMAL IMPORTS (safe after checks) ───────────────────────
import pytesseract
from pdf2image import convert_from_path
from piper import PiperVoice
import subprocess
import wave
from pathlib import Path
import tkinterdnd2 as tk
from tkinterdnd2 import TkinterDnD
from tkinter import filedialog, messagebox, ttk
import urllib.request
import time
import os
import threading