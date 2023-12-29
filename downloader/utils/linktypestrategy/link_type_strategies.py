from abc import ABC, abstractmethod

from downloader.tasks.default_task import default_download_media_ytdlp


class LinkStrategy(ABC):
    @abstractmethod
    def process_link(self, link, group_name):
        pass


class AudioLinkStrategy(LinkStrategy):
    def process_link(self, link, group_name):
        pass


class VideoLinkStrategy(LinkStrategy):
    def process_link(self, link, group_name):
        default_download_media_ytdlp(link, group_name)
