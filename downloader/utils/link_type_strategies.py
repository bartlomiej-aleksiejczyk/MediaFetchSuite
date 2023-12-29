from abc import ABC, abstractmethod

from downloader.tasks.default_task import default_download_media_ytdlp


class LinkStrategy(ABC):
    @abstractmethod
    def process_link(self, link_id):
        pass


class AudioLinkStrategy(LinkStrategy):
    def process_link(self, link_id):
        pass


class VideoLinkStrategy(LinkStrategy):
    def process_link(self, link):
        default_download_media_ytdlp(link)
