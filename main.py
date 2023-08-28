import os
import hashlib
import pytube
from typing import Tuple
import ffmpeg


YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=Fv_3IfieHuU&t=11s"
OUTPUT_PATH = "downloads"


def generate_hashed_path(default_filename: str) -> str:
    """
    Use sha256 to hash filename
    """
    return hashlib.sha256(default_filename.encode()).hexdigest()


def download_audio(url: str) -> Tuple[str, str]:
    """
    Download only audio from youtube video and save in .mp4 format
    """
    yt_video = pytube.YouTube(url)
    # Filter to download only audio
    audio_stream = yt_video.streams.filter(only_audio=True).first()

    # Generate hashed directory name and save in downloads
    directory = generate_hashed_path(audio_stream.default_filename)
    output_file_path = os.path.join(OUTPUT_PATH, directory)

    audio_file_path = audio_stream.download(output_path=output_file_path)
    return audio_file_path, directory


def process_to_wav(hashed_dir: str, file_name: str):
    """
    Process audio file in format .mp4 to .wav
    """
    input_file = ffmpeg.input(file_name)
    output_file = ffmpeg.output(
        input_file, "processed_audio.wav", acodec="pcm_s16le", ac=1, ar="16k"
    )
    ffmpeg.run(output_file)


if __name__ == "__main__":
    path, hashed_dir = download_audio(YOUTUBE_VIDEO_URL)
    print(f"File saved in {path} directory.")
