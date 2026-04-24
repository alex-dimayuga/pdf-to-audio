# PDF to Audio Converter

Senior design project for converting documents into spoken audio files through a desktop GUI.

This application lets a user drag and drop `.pdf` and `.docx` files into a queue, extract the document text, generate speech with a Piper voice model, and export the result as an `.mp3` file. The current implementation is written in Python with a Tkinter-based interface.

## Features

- Drag-and-drop desktop interface using `tkinter` and `tkinterdnd2`
- Queue multiple files for batch conversion
- Supports both `.pdf` and `.docx` input
- OCR-based PDF text extraction
- Text-to-speech generation with Piper
- MP3 export through `ffmpeg`
- Output folder selection from the GUI
- Automatic download of the Piper voice model if it is missing
- Background conversion thread so the GUI stays responsive during processing

## How It Works

1. The user adds one or more `.pdf` or `.docx` files.
2. The program extracts text from the selected document.
   - `.docx` files are read with `python-docx`
   - PDFs are processed with OCR
3. The extracted text is passed to the Piper TTS engine.
4. Piper generates a temporary `.wav` file.
5. `ffmpeg` converts the `.wav` into an `.mp3` file.
6. The temporary `.wav` is deleted after conversion.

## Project Structure

```text
pdf-to-audio-main/
├── app/
│   ├── gui.py                  # Tkinter drag-and-drop interface
│   └── pdf_audio_pipeline.py   # Text extraction and TTS pipeline
├── voice_model/
│   └── en_GB-cori-high.onnx.json
├── wip/                        # Experimental or in-progress files
├── requirements.txt            # Python dependencies
├── Plan.txt                    # Early planning notes
└── README.md                   # Project readme
```

## Dependencies

Core libraries used by the project include:

- `tkinter`
- `tkinterdnd2`
- `pytesseract`
- `PyMuPDF`
- `pdf2image`
- `Pillow`
- `piper-tts`
- `python-docx`
- `pydub`
- `ffmpeg` (system dependency)

Install Python packages with:

```bash
pip install -r requirements.txt
```

## External Requirements

This project also depends on system tools that are not fully handled by `pip` alone.

### 1. Tesseract OCR
Tesseract is required for OCR-based text extraction from PDFs.

- On Windows, the code checks common install paths for `tesseract.exe`
- On Linux, `tesseract` should be installed and available on the system path

### 2. ffmpeg
`ffmpeg` is required to convert the Piper-generated `.wav` file into `.mp3`.

Make sure `ffmpeg` is installed and accessible from the command line.

### 3. Poppler
On Linux, `pdf2image` may require Poppler utilities to convert PDF pages into images before OCR.

## Running the Application

From the project root, run:

```bash
python app/gui.py
```

The GUI will open and allow you to:

- drag and drop files into the queue
- browse for files manually
- choose an output folder
- convert all queued files into audio

## Current Behavior and Implementation Notes

- The GUI accepts both `.pdf` and `.docx` files
- Converted files are saved as `.mp3` using the original filename stem
- The Piper voice model is expected at:

```text
voice_model/en_GB-cori-high.onnx
```

- If the model is missing, the pipeline attempts to download it automatically
- File conversion runs in a worker thread so the interface does not fully freeze during processing

## Known Limitations

- PDF extraction is OCR-based, which may be slower than direct text extraction for digital PDFs
- Very large documents may take a long time to process
- Output is a single MP3 per input file with no chaptering or section splitting
- Error handling is basic and some failure messages are only surfaced after the batch finishes
- The current README and codebase suggest the project is still under active development
- The repository includes only the voice model JSON metadata, not necessarily the `.onnx` model file itself

## Future Improvements

- Detect and use direct text extraction for digital PDFs before falling back to OCR
- Split long documents into chunks for more efficient TTS generation
- Add pause, cancel, and per-file retry controls
- Improve progress reporting during extraction and audio generation
- Support more voice options and voice selection in the GUI
- Package the project as a standalone executable with PyInstaller
- Clean up temporary files and dependency checks more robustly

## Intended Use Case

This project is aimed at users who want to listen to written documents instead of reading them directly. Possible use cases include:

- accessibility support
- multitasking while listening to readings
- converting notes or reports into audio
- listening to scanned or text-based documents on the go

## Authors

Based on the source headers, the project authors are:

- Alex Dimayuga
- Alex Franzoni
- Caleb Burnett
- Caleb Harper
- Michael Naughton

## Status

Work in progress.
