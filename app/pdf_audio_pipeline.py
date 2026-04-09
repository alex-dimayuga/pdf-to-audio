"""
===============================================================================
Title       : pdf_audio_pipeline.py
Project     : PDF-TO-AUDIO
Authors     :   Alex Dimayuga
                Alex Franzoni
                Caleb Burnett
                Caleb Harper
                Michael Naughton
Last Edited : 4/8/2026
Description : Includes functions for extracting text from PDFs and Word 
              documents, and converting that text to audio using the Piper TTS 
              model. Handles both Windows and Linux PDF extraction, and ensures 
              the Piper model is downloaded and accessible. Creates output 
              audio files in a new folder named after the input document.

Dependencies: 
    - Python 3.8+
    - pytesseract (for OCR)
    - fitz (PyMuPDF, for PDF handling on Windows)
    - pdf2image (for PDF handling on Linux)
    - Pillow (for image processing)
    - piper (for text-to-speech conversion)

Usage:
    - Use the extract_text function to get text from a PDF or Word document by 
      passing the file path as a string.
    - Use the text_to_audio function to convert extracted text to audio by 
      passing the text and the desired output path for the audio file.

Notes:
    - Windows users must have Tesseract OCR installed and added to PATH for PDF
      extraction to work. 
    - WORK-IN-PROGRESS!
===============================================================================
"""
# Imports
# =============================================================================
import pytesseract
import subprocess
import wave
import tkinter as tk
import platform
import fitz 
from PIL import Image
from pdf2image import convert_from_path
from piper import PiperVoice
from pathlib import Path
from tkinter import filedialog
import urllib.request
from docx import Document
# =============================================================================

# Helper Functions
# =============================================================================
def word_to_text(path): 
    """ pass string of path to word doc, and returns extracted text. """
    # pass string of path to word doc, and returns extracted text.
    word_path = Path(path) # convert string to path

    word_doc = Document(word_path)
    # Extract text from all paragraphs
    full_text = []
    for paragraph in word_doc.paragraphs:
        full_text.append(paragraph.text)

    # Join all paragraphs into a single string
    text_content = '\n'.join(full_text)
    
    return text_content

# For new GUI
def extract_text(path: str) -> str:
    """expects a string, and returns the text of the passed document as a string."""
    text = ""

    pdf_path = Path(path) # convert string to path
    file_type = pdf_path.suffix.lower()

    # handle Word docs
    if (file_type == ".docx"):
        text = word_to_text(path) # pass string of path to word doc, and returns extracted text.

    # Handle Windows PDF extraction only if word doc not passed:
    if (platform.system() == "Windows") and (text == ""):
        doc = fitz.open(path) # open the pdf using fitz

        for page in doc: 
            pix = page.get_pixmap(dpi=300) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # convert to PIL image
            text += "\n" + pytesseract.image_to_string(img, config="--oem 3 --psm 4") + "\n" # use pytesseract to do OCR on the image and add it to the text variable
    
    # Handle Linux:
    elif (text == ""): # for linux, we can use pdf2image and pytesseract to do OCR on the pdf
        images = convert_from_path(path) # Use pdf2image to convert PDF pages to images

        # convert each page to pdf
        for image in images:
            # oem3 --psm4 is reccomended for scanned documents
            text += "\n" + pytesseract.image_to_string(image, config="--oem 3 --psm 4") + "\n"
    
    # implicit else, with returning text extraced from word doc.

    return text

def text_to_audio(text: str, out_path: str):
    voicepath = Path(__file__).resolve().parent.parent / "voice_model" / "en_GB-cori-high.onnx"

    # Ensure model is downloaded and accessible:
    if not voicepath.exists():
        try:
            urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx", voicepath)
            print("Model Downloaded! Converting file...")

        except urllib.error.URLError: # catch and notify the user to connect to the internet.
            print("Local Model Not installed. \n Download failed: No internet connection.")
            return

        except Exception as e:
            print("Download failed: Unknown error.")
            print("Error:", e)
            return

    voice = PiperVoice.load(voicepath)

    # Temporary WAV
    wav_path = Path(out_path).with_suffix(".wav")

    # Convert using tts
    with wave.open(str(wav_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    # Convert to mp3
    subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), str(out_path)],check=True)
 
    # Cleanup
    if wav_path.exists():
        wav_path.unlink()
# =============================================================================
