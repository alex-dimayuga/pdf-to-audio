"""
===============================================================================
Title       : main.py
Project     : PDF-TO-AUDIO
Authors     : 
Created     : 
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
# =============================================================================


def main():

    
    
    def convert_pdf(path):
        pdf_path = Path(path) # convert string to path

        # make a folder in the same directory as the pdf path
        output_folder = pdf_path.parent / f"{pdf_path.stem}_audio" # label it the name of the pdf + _audio
        output_folder.mkdir(exist_ok=True) # ensure file now exists.

        # only output to this new folder
        wav_path = output_folder / f"{pdf_path.stem}.wav"
        mp3_path = output_folder / f"{pdf_path.stem}.mp3"

        text = ""

        if platform.system() == "Windows":
            doc = fitz.open(path) # open the pdf using fitz

            for page in doc: 
                pix = page.get_pixmap(dpi=300) 
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # convert to PIL image
                text += "\n" + pytesseract.image_to_string(img, config="--oem 3 --psm 4") + "\n" # use pytesseract to do OCR on the image and add it to the text variable
        else: # for linux, we can use pdf2image and pytesseract to do OCR on the pdf
            images = convert_from_path(path) # Use pdf2image to convert PDF pages to images

            # convert each page to pdf
            for image in images:
                # oem3 --psm4 is reccomended for scanned documents
                text += "\n" + pytesseract.image_to_string(image, config="--oem 3 --psm 4") + "\n"

        
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

    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if not path:
            return

        status_label.config(text="Parsing PDF...")
        root.update_idletasks()

        output_folder, mp3_path = convert_pdf(path)

        # open the folder so user can see the mp3
        subprocess.run(["xdg-open", str(output_folder)])

        # close tkinter window
        root.destroy()

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

def convert_pdf_to_text(path):
    pdf_path = Path(path) # convert string to path
    text_output = []

    doc = fitz.open(pdf_path) 

    for page in doc:
        extracted_text = page.get_text().strip()

        if extracted_text: 
            # if text is not empty, add it to the text output list
            text_output.append(extracted_text)
            continue

        if platform.system() == "Windows":
            pix = page.get_pixmap(dpi=300) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # convert to PIL image
            text_output.append(pytesseract.image_to_string(img, config="--oem 3 --psm 4").strip()) # use pytesseract to do OCR on the image and add it to the text variable
        else:
            # Linux: use pdf2image to convert PDF pages to images, then use pytesseract to do OCR on the images
            images = convert_from_path(path)
            img = images[page.number] # get the corresponding image for the page
            text_output.append(pytesseract.image_to_string(img, config="--oem 3 --psm 4").strip()) # use pytesseract to do OCR on the image and add it to the text variable
    
    return "\n".join(text_output) # join the text output list into a single string and return it


if __name__ == "__main__":
    main()
