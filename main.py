import os
from pytube import YouTube
from pydub import AudioSegment
from fastapi import FastAPI, HTTPException, Query
from starlette.responses import FileResponse
import aiofiles
import requests

app = FastAPI()

async def download_youtube_audio(url, output_path='downloads'):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        audio_file_path = audio_stream.download(output_path)

        base, ext = os.path.splitext(audio_file_path)
        mp3_file_path = base + '.mp3'

        audio = AudioSegment.from_file(audio_file_path)
        audio.export(mp3_file_path, format='mp3')

        os.remove(audio_file_path)

        print(f"Audio downloaded and converted to MP3 successfully, saved to {mp3_file_path}")
        return mp3_file_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def download_youtube_video(url, output_path='downloads'):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        yt = YouTube(url)
        video_stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()

        video_file_path = video_stream.download(output_path)

        print(f"Video downloaded successfully and saved to {video_file_path}")
        return video_file_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def remove_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# Server management stuff ===
@app.get("/")
def read_root():
    return "/audio/m/{code} for audio, /video/m/{code} for video"

@app.get("/deploy")
def deploy():
    requests.get('https://api.render.com/deploy/srv-cq2hm2t6l47c73b626a0?key=BOH_-qChfhw')
    return "Deployed!"

@app.get("/reset")
def reset():
    remove_files_in_directory('downloads')
    return "Removed all downloaded files!"


# Downloadings ===
@app.get("/audio/m/{url}")
async def download_audio(url: str):
    file_path = await download_youtube_audio("https://m.youtube.com/watch?v=" + url)
    if file_path:
        return FileResponse(file_path, media_type='audio/mpeg', filename=os.path.basename(file_path))
    else:
        raise HTTPException(status_code=500, detail="Error downloading audio")

@app.get("/video/m/{url}")
async def download_video(url: str):
    file_path = await download_youtube_video("https://m.youtube.com/watch?v=" + url)
    if file_path:
        return FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))
    else:
        raise HTTPException(status_code=500, detail="Error downloading video")

@app.get("/watch/")
async def watch_video(v: str = Query(..., alias='v')):
    file_path = await download_youtube_video("https://m.youtube.com/watch?v=" + v)
    if file_path:
        return FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))
    else:
        raise HTTPException(status_code=500, detail="Error downloading video")

@app.get("/audio/watch/")
async def listen_audio(v: str = Query(..., alias='v')):
    file_path = await download_youtube_video("https://m.youtube.com/watch?v=" + v)
    if file_path:
        return FileResponse(file_path, media_type='video/mp4', filename=os.path.basename(file_path))
    else:
        raise HTTPException(status_code=500, detail="Error downloading video")
