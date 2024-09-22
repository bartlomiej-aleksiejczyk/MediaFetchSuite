import enum
import os
import re
import tempfile
import logging
import shutil
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

# Set up Django logger
logger = logging.getLogger(__name__)


def download_single_video_highest_quality(urls):
    """
    Downloads a single video at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info("Downloading single video with highest quality. URL: %s", urls)
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
            info_dict = ydl.extract_info(urls, download=True)
            if info_dict:
                filename = ydl.prepare_filename(info_dict)
                file_paths.append(filename)
                logger.info(f"Downloaded video to {filename}")
            else:
                error_message = "Failed to retrieve video information."
                logger.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading video: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_audios_from_list(urls_list):
    """
    Downloads audio files from a list of URLs, each separated by a newline.
    Uses the highest available quality for each audio.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info("Downloading audios from list.")

    # Split the list of URLs by newline and strip any extra spaces
    urlss = [urls.strip() for urls in urls_list.split("\n") if urls.strip()]

    all_file_paths = []
    for urls in urlss:
        logger.info(f"Processing URL: {urls}")
        result = download_single_audio_highest_quality(urls)
        if result["success"]:
            all_file_paths.extend(result["file_paths"])
        else:
            logger.error(f"Failed to download from URL: {urls}")
            return {"success": False, "error": result.get("error", "Unknown error")}

    return {"success": True, "file_paths": all_file_paths}


def download_videos_from_list(urls_list):
    """
    Downloads videos from a list of URLs, each separated by a newline.
    Uses the highest quality for each video.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info("Downloading videos from list.")

    urlss = [urls.strip() for urls in urls_list.split("\n") if urls.strip()]

    all_file_paths = []
    for urls in urlss:
        logger.info(f"Processing URL: {urls}")
        result = download_single_video_highest_quality(urls)
        if result["success"]:
            all_file_paths.extend(result["file_paths"])
        else:
            logger.error(f"Failed to download from URL: {urls}")
            return {"success": False, "error": result.get("error", "Unknown error")}

    return {"success": True, "file_paths": all_file_paths}


def download_video_playlist_highest_quality(urls):
    """
    Downloads a playlist of videos at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info(f"Downloading video playlist with highest quality. URL: {urls}")

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
            info_dict = ydl.extract_info(urls, download=True)
            if info_dict and "entries" in info_dict:
                for entry in info_dict["entries"]:
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        file_paths.append(filename)
                        logger.info(f"Downloaded video to {filename}")
                    else:
                        error_message = "Failed to retrieve information for one or more playlist entries."
                        logger.error(error_message)
                        shutil.rmtree(temp_dir)
                        return {"success": False, "error": error_message}
            else:
                error_message = "Failed to retrieve playlist information."
                logger.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading playlist: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_single_audio_highest_quality(urls):
    """
    Downloads a single audio track at the highest available quality.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info(f"Downloading single audio with highest quality. URL: {urls}")

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
            info_dict = ydl.extract_info(urls, download=True)
            if info_dict:
                file_paths = [
                    item["filepath"] for item in info_dict["requested_downloads"]
                ]
                logger.info(f"Downloaded audio to {file_paths}")
            else:
                error_message = "Failed to retrieve audio information."
                logger.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading audio: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}


def download_audio_playlist_highest_quality(urls):
    """
    Downloads an audio playlist at the highest available quality and converts it to MP3.
    Returns a dictionary with success status and list of file paths.
    """
    logger.info(f"Downloading audio playlist with highest quality. URL: {urls}")

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
            info_dict = ydl.extract_info(urls, download=True)
            if info_dict and "entries" in info_dict:
                for entry in info_dict["entries"]:
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        mp3_filename = re.sub(r"\.[^.]+$", ".mp3", filename)
                        file_paths.append(mp3_filename)
                        logger.info(f"Downloaded audio to {mp3_filename}")
                    else:
                        error_message = "Failed to retrieve information for one or more playlist entries."
                        logger.error(error_message)
                        shutil.rmtree(temp_dir)
                        return {"success": False, "error": error_message}
            else:
                error_message = "Failed to retrieve playlist information."
                logger.error(error_message)
                shutil.rmtree(temp_dir)
                return {"success": False, "error": error_message}
        return {"success": True, "file_paths": file_paths}
    except (DownloadError, ExtractorError) as e:
        error_message = f"Error downloading playlist: {e}"
        logger.error(error_message)
        shutil.rmtree(temp_dir)
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logger.error(error_message)
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
    VIDEO_LIST_HIGHEST = (
        "video_list_highest",
        "Downloads videos from a list of URLs separated by newlines using ytdlp at the highest available quality.",
        download_videos_from_list,
    )
    AUDIO_LIST_HIGHEST = (
        "audio_list_highest",
        "Downloads audios from a list of URLs separated by newlines using ytdlp at the highest available quality.",
        download_audios_from_list,
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
