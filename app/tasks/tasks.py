import sys
import shutil
from app import create_app
from editor.create_video import VideoCreator

app = create_app()
app.app_context().push()

def create_video_user_images(video_file_name, images_directory_path, temporary_directory, use_audio, audio_file_path, text_path):
    app.logger.info("Started create_video_user_images task")
    try:
        video_creator = VideoCreator(
            images_directory_path=images_directory_path,
            temporary_directory=temporary_directory,
            use_audio=use_audio,
            audio_file_path=audio_file_path,
            txtpath=text_path,
            usage_rights="any",
            output_file=f"app/static/videos/{video_file_name}.mp4",
            use_images=True,
        )
        video_creator.create_video()
        return video_file_name
    except:
        app.logger.error("Unhandled exception", exc_info = sys.exc_info())
    finally:
        shutil.rmtree(temporary_directory)
    
def create_video_no_images(video_file_name, images_directory_path, temporary_directory, use_audio, audio_file_path, text_path):
    app.logger.info("Started create_video_user_images task")
    try:
        creator = VideoCreator(
            images_directory_path=images_directory_path,
            temporary_directory=temporary_directory,
            use_audio=use_audio,
            audio_file_path=audio_file_path,
            txtpath=text_path,
            usage_rights="any",
            output_file=f"app/static/videos/{video_file_name}.mp4",
        )
        creator.create_video()
        return video_file_name
    except:
        app.logger.error("Unhandled exception", exc_info = sys.exc_info())
    finally:
        shutil.rmtree(temporary_directory)
