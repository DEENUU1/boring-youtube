import os
import hashlib
import pytube
from typing import Tuple
import ffmpeg
import whisper
from pydub import AudioSegment


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


def chunk(path: str):
    """
    Split long video into the n chunks
    """
    audio = AudioSegment.from_wav(path)

    print(f"Oryginal audio length is {len(audio)/1000} seconds")

    chunk_lenght = 300 * 1000  # 5 minuts (300 seconds)
    chunks = [audio[i : i + chunk_lenght] for i in range(0, len(audio), chunk_lenght)]

    for i, chunk in enumerate(chunks):
        chunk.export(f"chunk_{i}.wav", format="wav")

    print(f"Saved {len(chunks)} chunks")


if __name__ == "__main__":
    path, hashed_dir = download_audio(YOUTUBE_VIDEO_URL)
    print(f"File saved in {path} directory.")

    video_dir = find_folder(hashed_dir, OUTPUT_PATH)

    full_transcription = []
    # Try to make a transcription
    try:
        transcr = transcription(path)
        full_transcription.append(transcr)
    except RuntimeError:
        process_to_wav(path)
    except MemoryError:
        process_to_wav(path)

        # find all files in video_dir which starts from "chunk" and ends with ".wav"
        chunk_files = [
            os.path.join(video_dir, f)
            for f in os.listdir(video_dir)
            if f.startswith("chunk") and f.endswith(".wav")
        ]
        for chunk_file in chunk_files:
            transcr = transcription(chunk_file)
            full_transcription.append(transcr)

    # Split .wav file into chunks
    # Run transcription on each chunk
