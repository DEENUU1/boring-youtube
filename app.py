import customtkinter as ctk
from tkinter import messagebox
import re
from script import (
    download_audio,
    process_to_wav,
    chunk,
    transcription,
    return_text_chunk,
    find_folder,
    OUTPUT_PATH,
    llm_chain,
)
import os


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boring Youtube")
        self.geometry("600x400")
        self.resizable(False, False)

        self.url_entry = ctk.CTkEntry(self, font=("Helvetica", 16))
        self.url_entry.pack()

        text_label = ctk.CTkLabel(self, text="Some text...", font=("Helvetica", 16))
        text_label.pack(pady=20)

        run_button = ctk.CTkButton(self, text="Run", command=self.run_button_clicked)
        run_button.pack()

    def valid_url(self, url: str) -> bool:
        youtube_url_pattern = re.compile(
            r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)"
        )
        return bool(youtube_url_pattern.match(url))

    def run_button_clicked(self):
        url = self.url_entry.get()

        if not url or not self.valid_url(url):
            messagebox.showerror("Error", "Please enter a valid URL.")

        try:
            path, hashed_dir, length = download_audio(url)
            print(f"File saved in {path} directory.")

            video_dir = find_folder(hashed_dir, OUTPUT_PATH)

            full_transcription = []
            full_summary = []

            wav = process_to_wav(path)
            chunk(wav, video_dir)
            chunk_files = [
                os.path.join(video_dir, f)
                for f in os.listdir(video_dir)
                if f.startswith("chunk") and f.endswith(".wav")
            ]
            for chunk_file in chunk_files:
                transcr = transcription(chunk_file)
                print(transcr)
                full_transcription.append(transcr)

            text_str = " ".join(full_transcription)

            chunk_text = return_text_chunk(text_str)

            for idx, t in enumerate(chunk_text):
                summary = llm_chain.run(t)
                full_summary.append(summary)

                print(f"Summary {idx}/{len(chunk_text)}")
                print(summary)

            print(" ".join(full_summary))

        except Exception as e:
            messagebox.showerror("Error", str(e))
