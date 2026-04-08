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
# import tkinter as tk
# import subprocess
# from tkinter import filedialog
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from pdf_audio_pipeline import extract_text, text_to_audio
# =============================================================================

# Global Variables
# ==============================================================================
BG        = "#1a1a2e"
PANEL     = "#16213e"
ACCENT    = "#0f3460"
HIGHLIGHT = "#e94560"
TEXT      = "#eaeaea"
MUTED     = "#8892a4"
SUCCESS   = "#4caf83"
FONT_MAIN = ("Courier New", 11)
FONT_BIG  = ("Courier New", 13, "bold")
FONT_SM   = ("Courier New", 9)
# ==============================================================================

# GUI Class
# =============================================================================
class PDFToAudioApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF → Audio Converter")
        self.root.geometry("620x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.queued_files: list[str] = []
        self.output_dir: str = os.path.expanduser("~")
        self.is_converting = False

        self._build_ui()

        self._setup_drag_and_drop()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=HIGHLIGHT, height=4)
        title_frame.pack(fill="x")

        header = tk.Frame(self.root, bg=PANEL, pady=16)
        header.pack(fill="x")
        tk.Label(
            header, text="PDF  →  AUDIO",
            font=("Courier New", 20, "bold"),
            bg=PANEL, fg=TEXT
        ).pack()
        tk.Label(
            header, text="drag · drop · convert",
            font=FONT_SM, bg=PANEL, fg=MUTED
        ).pack()

        # Drop zone
        drop_frame = tk.Frame(self.root, bg=BG, pady=12, padx=20)
        drop_frame.pack(fill="x")

        self.drop_zone = tk.Label(
            drop_frame,
            text="⬇  drag PDF files here  ⬇",
            font=FONT_BIG,
            bg=ACCENT, fg=TEXT,
            relief="flat",
            padx=20, pady=30,
            cursor="hand2" 
        )
        self.drop_zone.pack(fill="x", ipady=10)

        # Buttons row
        btn_frame = tk.Frame(self.root, bg=BG, pady=8)
        btn_frame.pack()

        self._btn(btn_frame, "📂  Browse Files", self._browse_files,
                  HIGHLIGHT).pack(side="left", padx=6)
        self._btn(btn_frame, "📁  Set Output Folder", self._set_output_dir,
                  ACCENT).pack(side="left", padx=6)
        self._btn(btn_frame, "🗑  Clear Queue", self._clear_queue,
                  "#333355").pack(side="left", padx=6)

        # File queue
        queue_frame = tk.Frame(self.root, bg=BG, padx=20)
        queue_frame.pack(fill="both", expand=True)

        tk.Label(queue_frame, text="QUEUE", font=FONT_SM,
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(4, 2))

        list_bg = tk.Frame(queue_frame, bg=PANEL, relief="flat")
        list_bg.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_bg)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(
            list_bg,
            yscrollcommand=scrollbar.set,
            bg=PANEL, fg=TEXT,
            selectbackground=HIGHLIGHT,
            font=FONT_MAIN,
            relief="flat", bd=0,
            activestyle="none",
            height=8,
        )
        self.file_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        scrollbar.config(command=self.file_listbox.yview)

        # Output label
        self.output_label = tk.Label(
            self.root,
            text=f"Output → {self.output_dir}",
            font=FONT_SM, bg=BG, fg=MUTED,
            anchor="w"
        )
        self.output_label.pack(fill="x", padx=22, pady=(4, 0))

        # Progress bar
        prog_frame = tk.Frame(self.root, bg=BG, padx=20, pady=6)
        prog_frame.pack(fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Red.Horizontal.TProgressbar",
            troughcolor=PANEL,
            background=HIGHLIGHT,
            bordercolor=BG,
            lightcolor=HIGHLIGHT,
            darkcolor=HIGHLIGHT,
        )
        self.progress = ttk.Progressbar(
            prog_frame, style="Red.Horizontal.TProgressbar",
            mode="determinate", length=580
        )
        self.progress.pack(fill="x")

        self.status_label = tk.Label(
            self.root, text="Ready.",
            font=FONT_SM, bg=BG, fg=MUTED
        )
        self.status_label.pack(pady=(2, 0))

        # Convert button
        convert_frame = tk.Frame(self.root, bg=BG, pady=12)
        convert_frame.pack()

        self.convert_btn = self._btn(
            convert_frame, "▶  CONVERT TO AUDIO",
            self._start_conversion, HIGHLIGHT,
            big=True
        )
        self.convert_btn.pack()

    def _btn(self, parent, text, command, color, big=False):
        font = ("Courier New", 12, "bold") if big else FONT_MAIN
        pad = (28, 14) if big else (14, 8)
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color, fg=TEXT,
            font=font,
            relief="flat", bd=0,
            padx=pad[0], pady=pad[1],
            activebackground=HIGHLIGHT,
            activeforeground=TEXT,
            cursor="hand2",
        )
        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HIGHLIGHT))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        return btn

    # ── Drag-and-drop setup ───────────────────────────────────────────────────

    def _setup_drag_and_drop(self):
        """Register the drop zone and the file listbox as DnD targets."""
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self.drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave)

        # Also accept drops directly onto the list
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drag_enter(self, event):
        self.drop_zone.config(bg=HIGHLIGHT, fg=BG)

    def _on_drag_leave(self, event):
        self.drop_zone.config(bg=ACCENT, fg=TEXT)

    def _on_drop(self, event):
        self.drop_zone.config(bg=ACCENT, fg=TEXT)
        # tkinterdnd2 returns a space-separated list; braces wrap paths with spaces
        raw = event.data
        paths = self.root.tk.splitlist(raw)
        self._add_files(paths)

    # ── File handling ─────────────────────────────────────────────────────────

    def _browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        self._add_files(paths)

    def _add_files(self, paths):
        added = 0
        for path in paths:
            path = path.strip()
            if path.lower().endswith(".pdf") and path not in self.queued_files:
                self.queued_files.append(path)
                self.file_listbox.insert("end", f"  📄  {os.path.basename(path)}")
                added += 1
        if added:
            self._set_status(f"{added} file(s) added — {len(self.queued_files)} total in queue.")
        else:
            self._set_status("No new PDFs were added (already queued or not PDF).")

    def _clear_queue(self):
        self.queued_files.clear()
        self.file_listbox.delete(0, "end")
        self.progress["value"] = 0
        self._set_status("Queue cleared.")

    def _set_output_dir(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=f"Output → {self.output_dir}")

    # ── Conversion logic ──────────────────────────────────────────────────────

    def _start_conversion(self):
        if self.is_converting:
            return
        if not self.queued_files:
            messagebox.showwarning("No files", "Add at least one PDF to the queue first.")
            return
        # if not PDF_AVAILABLE or not GTTS_AVAILABLE:
        #     missing = []
        #     if not PDF_AVAILABLE: missing.append("pdfplumber")
        #     if not GTTS_AVAILABLE: missing.append("gtts")
        #     messagebox.showerror(
        #         "Missing libraries",
        #         f"Please install: pip install {' '.join(missing)}"
        #     )
        #     return

        self.is_converting = True
        self.convert_btn.config(state="disabled", text="⏳  Converting…")
        thread = threading.Thread(target=self._convert_all, daemon=True)
        thread.start()

    def _convert_all(self):
        total = len(self.queued_files)
        errors = []

        for i, pdf_path in enumerate(self.queued_files):
            name = os.path.basename(pdf_path)
            self._set_status(f"Converting {i+1}/{total}: {name}")

            try:
                text = extract_text(pdf_path)
                if not text.strip():
                    raise ValueError("No extractable text found in this PDF.")

                stem = os.path.splitext(name)[0]
                out_path = os.path.join(self.output_dir, f"{stem}.mp3")
                text_to_audio(text, out_path)

                # Highlight completed item in green
                self.file_listbox.itemconfig(i, fg=SUCCESS)
            except Exception as e:
                errors.append(f"{name}: {e}")
                self.file_listbox.itemconfig(i, fg=HIGHLIGHT)

            self.progress["value"] = ((i + 1) / total) * 100
            self.root.update_idletasks()

        self.is_converting = False
        self.root.after(0, self._on_conversion_done, errors)

    def _on_conversion_done(self, errors):
        self.convert_btn.config(state="normal", text="▶  CONVERT TO AUDIO")
        if errors:
            err_msg = "\n".join(errors)
            messagebox.showerror("Some files failed", f"Errors:\n\n{err_msg}")
            self._set_status(f"Done with {len(errors)} error(s). Check output folder.")
        else:
            self._set_status(f"✓ All files converted! Saved to: {self.output_dir}")
            messagebox.showinfo("Done!", f"All PDFs converted to MP3.\nSaved in:\n{self.output_dir}")

    def _set_status(self, msg: str):
        self.status_label.config(text=msg)
# =============================================================================

# Entry Point
# =============================================================================
def main():

    root = TkinterDnD.Tk()   # drag-and-drop-capable root
    app = PDFToAudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
# =============================================================================


# # GUI Class
# # =============================================================================
# class PDFToAudioGUI:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("PDF to MP3 Prototype")
#         self.root.geometry("1200x600")

#         self.button = tk.Button(self.root, text="Choose file", command=self.choose_file)
#         self.button.pack(pady=20)

#         self.status_label = tk.Label(
#             self.root,
#             text="Waiting for file...",
#             relief="ridge",
#             width=60,
#             height=10,
#             bg="white"
#         )
#         self.status_label.pack(padx=20, pady=20, fill="both", expand=True)

#     def choose_file(self):
#         path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf *.docx")])

#         if not path:
#             return

#         self.status_label.config(text="Converting File... \n This may take a few minutes.")
#         self.root.update_idletasks()

#         output_folder, mp3_path, status = convert_file(path)

#         self.status_label.config(text=status)

#         # open the folder so user can see the mp3
#         subprocess.run(["xdg-open", str(output_folder)])

#         # close tkinter window
#         self.root.destroy()

#     def run(self):
#         self.root.mainloop()
# # =============================================================================

# # Main Function
# # =============================================================================
# def main():
#     app = PDFToAudioGUI()
#     app.run()   

# if __name__ == "__main__":
#     main()
# # =============================================================================