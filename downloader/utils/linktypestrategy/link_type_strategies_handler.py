from downloader.utils.linktypestrategy.link_type_strategies import AudioLinkStrategy, VideoLinkStrategy
from mediafetchxpress import link_type_choices


def get_strategy(link_type):
    if link_type == link_type_choices.AUDIO:
        return AudioLinkStrategy()
    elif link_type == link_type_choices.VIDEO:
        return VideoLinkStrategy()
    else:
        raise ValueError(f"No strategy for link type: {link_type}")
