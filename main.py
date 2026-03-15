import pytesseract
from pdf2image import convert_from_path
from piper import PiperVoice
import subprocess
import wave
from pathlib import Path


def main():
    # when we drag and drop we need to just pass the file path to the function
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "LOTR.pdf"

    # convert PDF to images
    images = convert_from_path(pdf_path)

    #print("Pages converted:", len(images))

    # save the first page to check it
    images[0].save("first.png")
    print("saved first.png")

    # OCR
    text = pytesseract.image_to_string(images[0])

    print("Extracted text:")
    print(text)
    
    # get the string from a pdf scan.
    
    # This can be customized later, perhaps with lower quality or a scroll down menu. We could even have custom commands that install models with
    # samples of how they sound if we want.
    voice = PiperVoice.load("en_GB-cori-high.onnx")

    # pass the scanned text string into sytnhesizer 
    with wave.open("speech.wav", "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


    subprocess.run(["ffmpeg", "-y", "-i", "speech.wav", "speech.mp3"], check=True)

    # Seems to only output an mp3 of the first page of the passed pdf file.

if __name__ == "__main__":
    main()  
