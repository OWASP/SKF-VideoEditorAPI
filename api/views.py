from importlib.metadata import files
from flask import request, abort, jsonify
from werkzeug.datastructures import FileStorage

from app import app
from app.utils.utils import (
    check_for_err,
    create_tmp,
    get_tmp_paths,
    get_video_file_name,
    run_task
)

from app.tasks.tasks import create_video_no_images, create_video_user_images

from editor.create_video import VideoCreator
import traceback


@app.route("/", methods=["GET"])
def index():
    return "Home route"


@app.route("/upload-images", methods=["POST"])
def uplaod():
        if request.method == "POST":
            if request.files:
                POST = request.form
                use_audio: bool = POST.get("use_audio") == "true"
                usage_rights = POST.get("usage_rights")
                use_images: bool = POST.get("use_images") == "true"
                transcript: FileStorage = request.files["transcript"]
                if use_audio:
                    audio = request.files["audio"]
                else:
                    audio = None
                is_error, error_msg = check_for_err(
                    transcript=transcript, audio=audio, use_audio=use_audio)
                if is_error:
                    return abort(4000, description=error_msg)

                tmp_name = create_tmp()
                temporary_directory, images_directory_path, text_path, audio_file_path = get_tmp_paths(tmp_name)

                transcript.save(text_path)
                if use_audio:
                    audio.save(audio_file_path)

                if use_images:
                    word = ""
                    is_image = False
                    words = []
                    num_images = 0
                    with open(text_path, "r") as f:
                        for line in f:
                            for char in line:
                                if is_image:
                                    word += char
                                    if char == "]":
                                        words.append([word, True])
                                        num_images += 1
                                        word = ""
                                        is_image = False
                                elif char == "[":
                                    is_image = True
                                    if word != "":
                                        words.append([word, False])
                                    word = char
                                else:
                                    if char == " ":
                                        if word != "":
                                            words.append([word, False])
                                            word = ""
                                    else:
                                        word += char
                    if word != "":
                        words.append([word, False])
                    if is_image:
                        return abort(
                            4000, description="No closing bracket for image in transcript"
                        )
                    return {
                        "tmp_name": tmp_name,
                        "words": words,
                        "num_images": num_images
                    }
                else:
                    try:
                        video_file_name = get_video_file_name()
                        run_task(
                            create_video_no_images,
                            video_file_name=video_file_name,
                            images_directory_path=images_directory_path,
                            temporary_directory=temporary_directory,
                            use_audio=use_audio,
                            audio_file_path=audio_file_path,
                            text_path=text_path,
                            usage_rights=usage_rights,
                        )
                    except Exception as exc:
                        return abort(
                            500, description=str(exc)
                        )
                    return video_file_name
        if request.method == "POST" and request.files:
            POST = request.form
            use_audio: bool = POST.get("use_audio") == "true"
            usage_rights = POST.get("usage_rights")
            use_images: bool = POST.get("use_images") == "true"
            transcript: FileStorage = request.files["transcript"]
            if use_audio:
                audio = request.files["audio"]
            else:
                audio = None
            is_error, error_msg = check_for_err(
                transcript=transcript, audio=audio, use_audio=use_audio)
            if is_error:
                return abort(4000, description=error_msg)

            tmp_name = create_tmp()
            temporary_directory, images_directory_path, text_path, audio_file_path = get_tmp_paths(tmp_name)

            transcript.save(text_path)
            if use_audio:
                audio.save(audio_file_path)

            if use_images:
                word = ""
                is_image = False
                words = []
                num_images = 0
                with open(text_path, "r") as f:
                    for line in f:
                        for char in line:
                            if is_image:
                                word += char
                                if char == "]":
                                    words.append([word, True])
                                    num_images += 1
                                    word = ""
                                    is_image = False
                            elif char == "[":
                                is_image = True
                                if word != "":
                                    words.append([word, False])
                                word = char
                            else:
                                if char == " ":
                                    if word != "":
                                        words.append([word, False])
                                        word = ""
                                else:
                                    word += char
                if word != "":
                    words.append([word, False])
                if is_image:
                    return abort(
                        4000, description="No closing bracket for image in transcript"
                    )
                return {
                    "tmp_name": tmp_name,
                    "words": words,
                    "num_images": num_images
                }
            else:
                try:
                    video_file_name = get_video_file_name()
                    run_task(
                        create_video_no_images,
                        video_file_name=video_file_name,
                        images_directory_path=images_directory_path,
                        temporary_directory=temporary_directory,
                        use_audio=use_audio,
                        audio_file_path=audio_file_path,
                        text_path=text_path,
                        usage_rights=usage_rights,
                    )
                except Exception as exc:
                    return abort(
                        500, description=str(exc)
                    )
                return video_file_name

@app.route("/create-video", methods=["POST"])
def create():
    if request.method == "POST" and request.files:
        POST = request.form
        use_audio = POST.get("use_audio") == "true"
        tmp_name = POST.get("tmp_name")
        temporary_directory, images_directory_path, text_path, audio_file_path = get_tmp_paths(tmp_name)
        try:
            video_file_name = get_video_file_name()
            video_creator = VideoCreator(
                images_directory_path=images_directory_path,
                temporary_directory=temporary_directory,
                use_audio=use_audio,
                audio_file_path=audio_file_path,
                text_path=text_path,
                usage_rights="any",
                output_file=f"app/static/videos/{video_file_name}.mp4",
                use_images=True,
                images=request.files,
            )
            video_creator.create_setup_files()
            run_task(
                create_video_user_images,
                video_file_name=video_file_name,
                images_directory_path=images_directory_path,
                temporary_directory=temporary_directory,
                use_audio=use_audio,
                audio_file_path=audio_file_path,
                text_path=text_path
            )
        except Exception as exc:
            app.logger.error(traceback.format_exc())
            return abort(500, description=str(exc))
        return video_file_name
    return abort(400)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400
