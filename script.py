import os
import hashlib
import pytube
from typing import Tuple, List
import ffmpeg
import whisper
from pydub import AudioSegment
import textwrap
from dotenv import load_dotenv
from langchain import PromptTemplate, HuggingFaceHub, LLMChain


load_dotenv()

OUTPUT_PATH = "downloads"
TEMPLATE = "{text}"

PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["text"])
llm_chain = LLMChain(
    prompt=PROMPT,
    llm=HuggingFaceHub(
        repo_id="philschmid/bart-large-cnn-samsum",
        model_kwargs={"temperature": 0, "max_length": 64},
    ),
)


def generate_hashed_path(default_filename: str) -> str:
    """
    Use sha256 to hash filename
    """
    return hashlib.sha256(default_filename.encode()).hexdigest()


def download_audio(url: str) -> Tuple[str, str, int]:
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

    audio_length = yt_video.length
    return audio_file_path, directory, audio_length


def process_to_wav(path: str) -> str:
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

    return output_file_path


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


def chunk(input_path: str, save_path: str) -> None:
    """
    Split long video into the n chunks
    """
    audio = AudioSegment.from_wav(input_path)

    print(f"Oryginal audio length is {len(audio)/1000} seconds")

    chunk_lenght = 300 * 1000  # 5 minuts (300 seconds)
    chunks = [audio[i : i + chunk_lenght] for i in range(0, len(audio), chunk_lenght)]

    for i, chunk in enumerate(chunks):
        chunk.export(os.path.join(save_path, f"chunk_{i}.wav"), format="wav")

    print(f"Saved {len(chunks)} chunks")


def return_text_chunk(text: str) -> List[str]:
    """
    Split a large text into 4000 token objects in a list
    """
    return textwrap.wrap(text, 2000)
