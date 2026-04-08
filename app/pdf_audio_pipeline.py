"""
===============================================================================
Title       : main.py
Project     : PDF-TO-AUDIO
Authors     :   Alex Dimayuga
                Alex Franzoni
                Caleb Burnett
                Caleb Harper
                Michael Naughton
Version Date: 4/7/26 
Description : 

Dependencies:

Usage:

Notes:

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
import time
from docx import Document
# =============================================================================

# pass string of path to word doc, and returns extracted text.
def word_to_text(path): 
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
# -----------------------------------------------------------------------------
# expects a string, and returns the text of the passed document as a string.
def extract_text(path: str) -> str:
    text = ""


    pdf_path = Path(path) # convert string to path
    file_type = pdf_path.suffix.lower()

    # handle Word docs
    if (file_type == ".docx"):
        text = word_to_text(path) # pass string of path to word doc, and returns extracted text.

    # make a folder in the same directory as the pdf path
    output_folder = pdf_path.parent / f"{pdf_path.stem}_audio" # label it the name of the pdf + _audio
    output_folder.mkdir(exist_ok=True) # ensure file now exists.

    # only output to this new folder
    wav_path = output_folder / f"{pdf_path.stem}.wav"
    mp3_path = output_folder / f"{pdf_path.stem}.mp3"

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

    return text, wav_path, mp3_path, output_folder
# -----------------------------------------------------------------------------


def main():
    # -----------------------------------------------------------------------------
    def convert_file(path):
        # extract text from file in file path:
        text, wav_path, mp3_path, output_folder = extract_text(path)
        #text -> extracted text 
        #wav_path
        #mp3_path 
        #output_folder 

        # Ensure the AI model is downloaded and accessible:
        voicepath = Path("en_GB-cori-high.onnx")

        # catch and notify the user to connect to the internet.
        if not voicepath.exists():
            try:
                urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx", voicepath)
                status_label.config(text="Model Downloaded! Converting file...")

            except urllib.error.URLError: # catch and notify the user to connect to the internet.
                status_label.config(text="Local Model Not installed. \n Download failed: No internet connection.")
                return

            except Exception as e:
                status_label.config(text="Download failed: Unknown error.")
                print("Error:", e)
                return


        voice = PiperVoice.load(voicepath)

        # convert using tts
        with wave.open(str(wav_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        # place in the folder
        subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), str(mp3_path)],check=True)

        # remove the wav file
        if wav_path.exists():
            wav_path.unlink()
        return output_folder, mp3_path
    # -----------------------------------------------------------------------------
    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf *.docx")])

        if not path:
            return

        status_label.config(text="Converting File... \n This may take a few minutes.")
        root.update_idletasks()

        output_folder, mp3_path = convert_file(path)

        # open the folder so user can see the mp3
        subprocess.run(["xdg-open", str(output_folder)])

        # close tkinter window
        root.destroy()
    # -----------------------------------------------------------------------------
    root = tk.Tk()
    root.title("PDF to MP3 Prototype")
    root.geometry("1200x600")

    button = tk.Button(root, text="Choose file", command=choose_file)
    button.pack(pady=20)

    status_label = tk.Label(
        root,
        text="Waiting for file...",
        relief="ridge",
        width=60,
        height=10,
        bg="white"
    )
    status_label.pack(padx=20, pady=20, fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
