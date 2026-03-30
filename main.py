import pytesseract
from pdf2image import convert_from_path
from piper import PiperVoice
import subprocess
import wave
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


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
        images = convert_from_path(path)

        # convert each page to pdf
        for image in images:
            # oem3 --psm4 is reccomended for scanned documents
            text += "\n" + pytesseract.image_to_string(image, config="--oem 3 --psm 4") + "\n"

        voice = PiperVoice.load("en_GB-cori-high.onnx")

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

        status_label.config(text="Converting...")
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


if __name__ == "__main__":
    main()
