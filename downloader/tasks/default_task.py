from huey.contrib.djhuey import task
import pickle
from mediafetchxpress.models import Link, Event
import yt_dlp


@task()
def default_download_media_ytdlp(link_id):
    link = Link.objects.get(id=link_id)
    try:
        c = yt_dlp.YoutubeDL().download([link.url])
        print(type(c))
        print(len(c))
        link.delete()
        with open('test', 'wb') as output:
            pickle.dump(c, output, pickle.HIGHEST_PROTOCOL)

    except Exception as e:
        Event.objects.create(message=str(e))
