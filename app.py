import customtkinter as ctk
from tkinter import messagebox, Canvas, Scrollbar, VERTICAL
from script import (
    download_audio,
    process_to_wav,
    chunk,
    transcription,
    return_text_chunk,
    find_folder,
    OUTPUT_PATH,
    llm_chain,
    valid_url,
    update_full_text,
    save_to_txt,
    return_filename,
)
import os


full_text = []
full_transcription = []
full_summary = []


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window app settings
        self.title("Boring Youtube")
        self.geometry("1000x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")

        # Frame to paste the Youtube video URL
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(pady=10)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            font=("Helvetica", 16),
            width=400,
            placeholder_text="Youtube video URL",
        )
        self.url_entry.pack(side="left")

        # Button to run script
        run_button = ctk.CTkButton(self, text="Run", command=self.run_button_clicked)
        run_button.pack(pady=10)

        # Text box to display transcription and summary
        self.canvas = Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.text_label = self.canvas.create_text(
            10,
            10,
            anchor="nw",
            font=("Helvetica", 16),
            text="Please wait...",
            width=760,
            fill="black",
        )

        # Scrollbar to scroll down the text box
        scrollbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

    def run_button_clicked(self):
        """
        Button to run script
        """
        url = self.url_entry.get()

        if not url or not valid_url(url):
            messagebox.showerror("Error", "Please enter a valid URL.")

        try:
            path, hashed_dir, length = download_audio(url)
            filename = return_filename(path.replace(" ", ""))

            messagebox.showinfo("Success", f"Downloaded audio file to {path}")

            # Check if video length is less than 20 minutes
            # If video is more than 20 minutes it process video file into .wav file and than chunk the video into 5 minutes chunks
            if length <= 20:
                # Make transcription
                transcr = transcription(path)

                full_transcription.append(transcr)
                update_full_text(full_text, transcr)

                # Update text_label in tkinter app
                self.canvas.itemconfig(self.text_label, text=full_text)
                self.update()

                text_str = " ".join(full_transcription)
                # Save transcription to .txt file
                save_to_txt(text_str, f"transcription_{filename}.txt")

                # Chunk text into 2000 words
                chunk_text = return_text_chunk(text_str)

                # Make summary
                for t in chunk_text:
                    summary = llm_chain.run(t)

                    full_summary.append(summary)
                    update_full_text(full_text, summary)

                    # Update text_label in tkinter app
                    self.canvas.itemconfig(self.text_label, text=full_text)
                    self.update()

                full_summary_str = "".join(full_summary)
                # Save summary to .txt file
                save_to_txt(full_summary_str, f"summary_{filename}.txt")

            else:
                # Process to wav and chunk the video
                video_dir = find_folder(hashed_dir, OUTPUT_PATH)
                wav = process_to_wav(path)
                chunk(wav, video_dir)
                chunk_files = [
                    os.path.join(video_dir, f)
                    for f in os.listdir(video_dir)
                    if f.startswith("chunk") and f.endswith(".wav")
                ]

                # Make transcription
                for chunk_file in chunk_files:
                    transcr = transcription(chunk_file)

                    full_transcription.append(transcr)
                    update_full_text(full_text, transcr)

                    # Update text_label in tkinter app
                    self.canvas.itemconfig(self.text_label, text=full_text)
                    self.update()

                text_str = " ".join(full_transcription)
                # Save transcription to .txt file
                save_to_txt(text_str, f"transcription_{filename}.txt")

                # Chunk text into 2000 words
                chunk_text = return_text_chunk(text_str)

                # Make summary
                for t in chunk_text:
                    summary = llm_chain.run(t)

                    full_summary.append(summary)
                    update_full_text(full_text, summary)

                    # Update text_label in tkinter app
                    self.canvas.itemconfig(self.text_label, text=full_text)
                    self.update()

                full_summary_str = "".join(full_summary)
                # Save summary to .txt fil
                save_to_txt(full_summary_str, f"summary_{filename}.txt")

        except Exception as e:
            messagebox.showerror("Error", str(e))
