"""
===============================================================================
Title       : 
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
import tkinter as tk
import subprocess
from tkinter import filedialog
from pdf_audio_pipeline import convert_file
# =============================================================================

# GUI Class
# =============================================================================
class PDFToAudioGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF to MP3 Prototype")
        self.root.geometry("1200x600")

        self.button = tk.Button(self.root, text="Choose file", command=self.choose_file)
        self.button.pack(pady=20)

        self.status_label = tk.Label(
            self.root,
            text="Waiting for file...",
            relief="ridge",
            width=60,
            height=10,
            bg="white"
        )
        self.status_label.pack(padx=20, pady=20, fill="both", expand=True)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf *.docx")])

        if not path:
            return

        self.status_label.config(text="Converting File... \n This may take a few minutes.")
        self.root.update_idletasks()

        output_folder, mp3_path, status = convert_file(path)

        self.status_label.config(text=status)

        # open the folder so user can see the mp3
        subprocess.run(["xdg-open", str(output_folder)])

        # close tkinter window
        self.root.destroy()

    def run(self):
        self.root.mainloop()
# =============================================================================

# Main Function
# =============================================================================
def main():
    app = PDFToAudioGUI()
    app.run()   

if __name__ == "__main__":
    main()