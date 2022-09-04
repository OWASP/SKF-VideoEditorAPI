import os
import string
import random
import shutil
from typing import Callable
from editor.create_video import VideoCreator
from app.exception.exceptions import FailedAlignmentError
from flask import current_app
from app import app

def get_filename(length):
    chars = string.ascii_letters
    filename = "".join([random.choice(chars) for _ in range(length)])
    return filename

def get_video_file_name():
    video_file_name = get_filename(10)
    while os.path.isfile(f"app/static/videos/{video_file_name}.mp4"):
        video_file_name = get_filename(10)
    return video_file_name

def create_tmp():
    tmp_name= get_filename(10)
    while os.path.isdir(f"tmp/{tmp_name}"):
        tmp_name = get_filename(10)
    
    temporary_directory = os.path.join(os.getcwd(), "tmp", tmp_name)
    images_directory_path = os.path.join(temporary_directory, "images")
    os.makedirs(images_directory_path)
    return tmp_name

def get_tmp_paths(tmp_name: str):
    temporary_directory = os.path.join(os.getcwd(), "tmp", tmp_name)
    images_directory_path = os.path.join(temporary_directory, "images")
    text_path = os.path.join(temporary_directory, "text.txt")
    audio_file_path = os.path.join(temporary_directory, "audio.mp3")

    return temporary_directory, images_directory_path, text_path, audio_file_path

def check_for_err(transcript, audio, use_audio):
    TRANSCRIPT_EXT = [".txt", ".pdf"]
    AUDIO_EXT = [".mp3"]

    if transcript.filename == "":
        return True, "Missing Transcript"
    _, ext = os.path.splitext(transcript.filename)
    if(ext not in TRANSCRIPT_EXT):
        return True, f"Transcript can not have a {ext} file extension"

    if use_audio : 
        if audio.filename == "":
            return True, "Missing Audio file"
        
        _, ext = os.path.splitext(audio.filename)
        if ext not in AUDIO_EXT:
            return True, f"Audio cannot have a {ext} file extension"
    
    return False, None


def create_video(
    video_file_name,
    images_directory_path,
    temporary_directory,
    use_audio,
    audio_file_path,
    text_path,
    usage_rights,
    use_images=False,
    images=None
):
    creator = VideoCreator(
        images_directory_path=images_directory_path,
        temporary_directory=temporary_directory,
        use_audio=use_audio,
        audio_file_path=audio_file_path,
        txtpath=text_path,
        usage_rights=usage_rights,
        output_file=f"app/static/videos/{video_file_name}.mp4",
        use_images=use_images,
        images=images
    )

    try:
        creator.create_full_video()
    except FailedAlignmentError as exc:
        raise Exception("Could not alignt the audio with the script. Please try recording the audio again.") from exc
    finally:
        shutil.rmtree(temporary_directory)



def run_task(function: Callable, *args, **kwargs):
    app.logger.info(f'Task named "{function.__name__}" queued')
    current_app.task_queue.enqueue(function, *args, **kwargs)


