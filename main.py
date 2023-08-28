import os
import hashlib
import pytube
from typing import Tuple
import ffmpeg
import whisper


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


def process_to_wav(path: str):
    """
    Process audio file in format .mp4 to .wav
    """
    input_file = ffmpeg.input(path)

    folder_path, file_name = os.path.split(path)
    output_file_path = os.path.join(
        folder_path, os.path.splitext(file_name)[0] + ".wav"
    )

    output_file = ffmpeg.output(
        input_file, output_file_path, acodec="pcm_s16le", ac=1, ar="16k"
    )

    ffmpeg.run(output_file)


def transcription(filename: str) -> str:
    """
    Generate a transcription of a audio file
    """
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"]


def find_folder(folder_name, search_path):
    """
    Search for folder in specified directory
    """
    for item in os.listdir(search_path):
        item_path = os.path.join(search_path, item)
        if os.path.isdir(item_path):
            if item == folder_name:
                return item_path
            else:
                result = find_folder(folder_name, item_path)
                if result:
                    return result
    return None


if __name__ == "__main__":
    path, hashed_dir = download_audio(YOUTUBE_VIDEO_URL)
    print(f"File saved in {path} directory.")

    video_dir = find_folder(hashed_dir, OUTPUT_PATH)

    # Try to make a transcription
    try:
        transcr = transcription(path)
    except RuntimeError:
        process_to_wav(path)
    except MemoryError:
        process_to_wav(path)

    # if RuntimeError occurs:
    # process file to .wav file
    # Split .wav file into chunks
    # Run transcription on each chunk
