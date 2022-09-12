import os
import subprocess
import concurrent.futures
from app.exception.exceptions import FailedAlignmentError
from random import choice
import requests
from PIL import Image
from gtts import gTTS
from mutagen.mp3 import MP3
from werkzeug.utils import secure_filename
from google_images_download import google_images_download


class ImageCreator:

    def __init__(self, images_directory_path, usage_rights, use_images=False, images=None):
        self.images_directory_path = images_directory_path
        self.usage_rights = usage_rights
        self.use_images = use_images
        if use_images:
            self.images = images

    def download_images(self, image_words: list):
      
        if not self.use_images:
            response = google_images_download.googleimagesdownload()
            results = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i, search in enumerate(image_words):
                    arguments = {
                        "keywords": search,
                        "limit": 5,
                        "print_urls": False,
                        "output_directory": self.images_directory_path,
                        "image_directory": str(i),
                        "format": "jpg",
                        "chromedriver": "chromedriver.exe",
                        "silent_mode": True,
                    } 

                    if self.usage_rights != "any":
                        arguments["usage_rights"] = self.usage_rights
                    results.append(executor.submit(response.download, arguments))
        else:
            num_images = len(image_words)
            for i in range(0, num_images):
                image_dir = os.path.join(self.images_directory_path, str(i))
                os.mkdir(image_dir)
                self.images[str(i)].save(
                    os.path.join(
                        image_dir, secure_filename(self.images[str(i)].filename)
                    )
                )

    @classmethod
    def get_random_image(cls, image_dir):
        return os.path.join(image_dir, choice(os.listdir(image_dir)))

    @classmethod
    def convert_img(cls, image_path, new_ext=".jpg"):
        pre, ext = os.path.splitext(image_path)
        im = Image.open(image_path)
        rgb_im = im.convert("RGB")
        os.remove(image_path)
        rgb_im.save(pre + new_ext)
        return pre + new_ext

    @classmethod
    def resize_img(cls, image_path, newsize=(1920, 1080)):
        im = Image.open(image_path)
        im = im.resize(newsize)
        im.save(image_path)

    @classmethod
    def process_img(cls, image_path, newsize=(1920, 1080), new_ext=".jpg"):
        newpath = cls.convert_img(image_path, new_ext)
        cls.resize_img(newpath, newsize)
        return newpath

    def write_frames(self, words, prev_words, temporary_directory, image_words, audio_length):
        idx = 0
        prev_timestamp = 0
        timestamp = 0
        with open(os.path.join(temporary_directory, "frames.txt"), "w") as f:
            for i, word in enumerate(words):
                if idx + 1 < len(prev_words):
                    if i == prev_words[idx + 1]:
                        if word["case"] == "not-found-in-audio":
                            raise FailedAlignmentError
                        timestamp = word["end"]
                        try:
                            img = self.get_random_image(
                                os.path.join(self.images_directory_path, str(idx))
                            )
                        except IndexError:
                            raise ValueError(
                                f"No images downloaded for '{image_words[idx]}'"
                            )

                        newpath = self.process_img(img)
                        f.write(f"file '{newpath}'\n")
                        f.write(f"duration {timestamp - prev_timestamp}\n")
                        prev_timestamp = timestamp
                        idx += 1
                else:
                    break

            timestamp = audio_length
            try:
                img = self.get_random_image(os.path.join(self.images_directory_path, str(idx)))
            except IndexError:
                raise ValueError(f"No images downloaded for '{image_words[idx]}'")

            newpath = self.process_img(img)
            f.write(f"file '{newpath}'\n")
            f.write(f"duration {timestamp - prev_timestamp}\n")
            f.write(f"file '{newpath}'")


class VideoCreator:
    def __init__(self,images_directory_path,temporary_directory,use_audio,audio_file_path,text_path,usage_rights,output_file,use_images=False,images=None,):
        self.img_creator = ImageCreator(images_directory_path, usage_rights, use_images, images)
        self.temporary_directory = temporary_directory
        self.images_directory_path = images_directory_path
        self.use_audio = use_audio
        self.audio_file_path = audio_file_path
        self.text_path = text_path
        self.output_file = output_file

    def _get_audio_length(self):
        audio = MP3(self.audio_file_path)
        return audio.info.length

    def create_full_video(self):
        self.create_setup_files()
        self.create_video()

    def create_setup_files(self):
        image_words, prev_words, text = self.parse_transcript(self.text_path)
        parsed_txt_path = os.path.join(self.temporary_directory, "parsed.txt")
        with open(parsed_txt_path, "w", encoding="utf8") as f:
            f.write(text)

        if not self.use_audio:
            self.audio_file_path = os.path.join(self.temporary_directory, "audio.mp3")
            self.create_audio(text)

        self.img_creator.download_images(image_words)

        words = self.get_gentle_response(parsed_txt_path)

        audio_length = self._get_audio_length()
        self.img_creator.write_frames(words, prev_words, self.temporary_directory, image_words, audio_length)

    def create_video(self):
        self.combine_images()
        self.add_audio()
        self.convert_video()

    def combine_images(self):
        command = f"ffmpeg -safe 0 -y -f concat -i {os.path.join(self.temporary_directory, 'frames.txt')} {os.path.join(self.temporary_directory, 'video.mp4')}"
        subprocess.run(command, shell=True)

    def add_audio(self):
        command = f"ffmpeg -i {os.path.join(self.temporary_directory, 'video.mp4')} -i {self.audio_file_path} -c:v copy -c:a aac -y {os.path.join(self.temporary_directory, 'video_with_audio.mp4')}"
        subprocess.run(command, shell=True)

    def convert_video(self):
        command = f"ffmpeg -i {os.path.join(self.temporary_directory, 'video_with_audio.mp4')} -vcodec libx264 -preset ultrafast {self.output_file}"
        subprocess.run(command, shell=True)

    def create_audio(self, text):
        tts = gTTS(text)
        tts.save(self.audio_file_path)

    @classmethod
    def parse_transcript(cls, transcript_path: str):
        def get_last_word(text):
            words = text.split()
            return len(words) - 1

        image_words = []
        prev_words = []
        image_word = ""
        is_image = False
        parsed_text = ""
        with open(transcript_path, "r") as f:
            for line in f:
                for char in line:
                    if is_image:
                        if char == "]":
                            prev_word = get_last_word(parsed_text)
                            prev_words.append(prev_word)
                            image_words.append(image_word)
                            image_word = ""
                            is_image = False
                        else:
                            image_word += char
                    elif char == "[":
                        is_image = True
                    else:
                        parsed_text += char
        if is_image:
            msg = "No closing bracket for image in transcript"
            raise ValueError(msg)

        return image_words, prev_words, parsed_text

    def get_gentle_response(self, parsed_txt_path):
        with open(parsed_txt_path, "rb") as transcript:
            with open(self.audio_file_path, "rb") as audio:
                files = {"transcript": transcript, "audio": audio}
                r = requests.post("http://gentle:8765/transcriptions?async=false", files=files)
                gentle_json = r.json()
                words = gentle_json["words"]
                return words
