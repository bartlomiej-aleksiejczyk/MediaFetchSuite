import enum
import os
import re
import tempfile
import logging
import shutil
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError


def download_single_video_highest_quality(url):
    """
    Downloads a single video at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    print(f"Downloading single video with highest quality. URL: {url}")

    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
    }

    file_paths = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if info_dict:
                filename = ydl.prepare_filename(info_dict)
                file_paths.append(filename)
                print(f"Downloaded video to {filename}")
            else:
                error_message = "Failed to retrieve video information."
                logging.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading video: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_video_playlist_highest_quality(url):
    """
    Downloads a playlist of videos at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    print(f"Downloading video playlist with highest quality. URL: {url}")

    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(playlist_index)s-%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
    }

    file_paths = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if info_dict and "entries" in info_dict:
                for entry in info_dict["entries"]:
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        file_paths.append(filename)
                        print(f"Downloaded video to {filename}")
                    else:
                        error_message = "Failed to retrieve information for one or more playlist entries."
                        logging.error(error_message)
                        shutil.rmtree(temp_dir)
                        return {"success": False, "error": error_message}
            else:
                error_message = "Failed to retrieve playlist information."
                logging.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading playlist: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_single_audio_highest_quality(url):
    """
    Downloads a single audio track at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    print(f"Downloading single audio with highest quality. URL: {url}")

    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # This indicates the highest quality
            }
        ],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
    }

    file_paths = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if info_dict:
                file_paths = [
                    item["filepath"] for item in info_dict["requested_downloads"]
                ]
                print(f"Downloaded audio to {file_paths}")
            else:
                error_message = "Failed to retrieve audio information."
                logging.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading audio: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_audio_playlist_highest_quality(url):
    """
    Downloads an audio playlist at the highest available quality and converts it to MP3.
    Returns a dictionary with success status and list of file paths.
    """
    print(f"Downloading audio playlist with highest quality. URL: {url}")

    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(playlist_index)s-%(title)s.%(ext)s"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # This indicates the highest quality
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
    }

    file_paths = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if info_dict and "entries" in info_dict:
                for entry in info_dict["entries"]:
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        mp3_filename = re.sub(r"\.[^.]+$", ".mp3", filename)
                        file_paths.append(mp3_filename)
                        print(f"Downloaded audio to {mp3_filename}")
                    else:
                        error_message = "Failed to retrieve information for one or more playlist entries."
                        logging.error(error_message)
                        shutil.rmtree(temp_dir)
                        return {"success": False, "error": error_message}
            else:
                error_message = "Failed to retrieve playlist information."
                logging.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading playlist: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


class MediaDownloadStrategies(enum.Enum):
    AUDIO_HIGHEST = (
        "audio_highest",
        "Downloads single audios using ytdlp with highest available quality.",
        download_single_audio_highest_quality,
    )
    AUDIO_PLAYLIST_HIGHEST = (
        "audio_playlist_highest",
        "Downloads audio playlist using ytdlp with highest available quality.",
        download_audio_playlist_highest_quality,
    )
    VIDEO_HIGHEST = (
        "video_highest",
        "Downloads single videos using ytdlp with highest available quality.",
        download_single_video_highest_quality,
    )
    VIDEO_PLAYLIST_HIGHEST = (
        "video_playlist_highest",
        "Downloads playlist using ytdlp with highest available quality.",
        download_video_playlist_highest_quality,
    )

    def __new__(cls, value, description, strategy_function):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.strategy_function = strategy_function
        return obj

    @classmethod
    def choices(cls):
        """Get a list of available strategies and their descriptions."""
        return [(key.value, key.description) for key in cls]

    @classmethod
    def get_strategy_function(cls, value):
        """Retrieve the appropriate download strategy function."""
        for item in cls:
            if item.value == value:
                return item.strategy_function
        raise ValueError(f"No strategy function found for value: {value}")
