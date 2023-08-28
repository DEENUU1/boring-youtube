import os

import pytube

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=Fv_3IfieHuU&t=11s"
OUTPUT_PATH = "downloads"


def download_audio(url):
    """
    Download only audio from youtube video and save in .mp4 format
    """
    yt_video = pytube.YouTube(url)
    audio_stream = yt_video.streams.filter(only_audio=True).first()
    audio_file_path = audio_stream.download(output_path=OUTPUT_PATH)

    return audio_file_path


if __name__ == "__main__":
    da = download_audio(YOUTUBE_VIDEO_URL)
    print(f"File saved in {da} directory.")
