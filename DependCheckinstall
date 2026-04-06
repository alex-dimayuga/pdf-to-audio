import subprocess
import sys
import shutil
import urllib.request
from pathlib import Path

def check_and_install():
    # ── PIP PACKAGES ──────────────────────────────────────────────
    pip_packages = {
        "pytesseract": "pytesseract",
        "pdf2image":   "pdf2image",
        "piper":       "piper-tts",
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
    print("\nChecking system binaries...")
    binaries = {
        "tesseract": (
            "Tesseract OCR",
            "https://github.com/UB-Mannheim/tesseract/wiki"
        ),
        "ffmpeg": (
            "FFmpeg",
            "https://ffmpeg.org/download.html"
        ),
        "pdftoppm": (
            "Poppler (required by pdf2image)",
            "https://github.com/oschwartz10612/poppler-windows/releases"
        ),
    }

    missing = []
    for binary, (friendly_name, url) in binaries.items():
        if shutil.which(binary):
            print(f"  ✔ {friendly_name}")
        else:
            print(f"  ✘ {friendly_name} not found")
            missing.append((friendly_name, url))

    if missing:
        print("\n⚠ Missing system dependencies — please install manually:")
        for name, url in missing:
            print(f"  • {name}: {url}")
        input("\nPress Enter to continue anyway, or close this window to exit...")

    # ── PIPER VOICE MODEL FILES ────────────────────────────────────
    # Piper requires BOTH the .onnx model AND the .onnx.json config to run.
    print("\nChecking Piper voice model files...")

    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high"
    model_files = {
        "en_GB-cori-high.onnx":      f"{base_url}/en_GB-cori-high.onnx",
        "en_GB-cori-high.onnx.json": f"{base_url}/en_GB-cori-high.onnx.json",
    }

    for filename, url in model_files.items():
        filepath = Path(filename)
        if filepath.exists():
            print(f"  ✔ {filename}")
        else:
            print(f"  ✘ {filename} not found — downloading...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"  ✔ {filename} downloaded")
            except urllib.error.URLError:
                print(f"  ✘ Download failed: No internet connection.")
                print(f"    Please download manually from:\n    {url}")
                input("\nPress Enter to continue anyway, or close this window to exit...")
            except Exception as e:
                print(f"  ✘ Download failed: {e}")
                input("\nPress Enter to continue anyway, or close this window to exit...")

    print("\nAll checks done. Starting app...\n")


check_and_install()


