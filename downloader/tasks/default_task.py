import os

from huey.contrib.djhuey import task
from yt_dlp import YoutubeDL

from downloader.services.s3_handler import upload_downloaded_file_to_s3
from mediafetchxpress.models import Event


@task()
def default_download_media_ytdlp(link, group_name):
    try:

        # Set the directory where the file will be saved
        download_directory = 'downloads'
        file_path = os.path.join(download_directory, "%(title)s [%(id)s].%(ext)s")

        # Configure yt_dlp with output template
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path
        }

        # Download video
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link.url])

        # Assuming the download was successful, access the file
        downloaded_file_path = find_downloaded_file(download_directory)

        if downloaded_file_path:
            process_downloaded_file(downloaded_file_path, group_name)
            link.delete()
            os.remove(downloaded_file_path)
        else:
            raise Exception("Downloaded file not found")

    except Exception as e:
        Event.objects.create(message=f'Error in downloading or processing media: {str(e)}')


def find_downloaded_file(download_directory):
    """
    Find the most recently downloaded file in the specified directory.
    """
    try:
        # Get list of files sorted by creation time
        files = [os.path.join(download_directory, f) for f in os.listdir(download_directory)]
        files.sort(key=lambda x: os.path.getctime(x), reverse=True)

        # Return the most recently created file
        if files:
            return files[0]
    except Exception as e:
        print(f"Error finding downloaded file: {e}")

    return None


def process_downloaded_file(file_path, bucket_name):
    """
    Process the downloaded file.
    Example: read, move, upload, etc.
    """
    # Example: Just printing the file path
    print(f"Processing file: {file_path}")
    upload_downloaded_file_to_s3(file_path, bucket_name)
    # Add your file processing logic here
