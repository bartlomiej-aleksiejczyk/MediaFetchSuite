# Generated by Django 5.0.6 on 2024-09-22 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0005_alter_downloadtask_download_strategy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadtask',
            name='download_strategy',
            field=models.CharField(choices=[('audio_highest', 'Downloads single audios using ytdlp with highest available quality.'), ('audio_playlist_highest', 'Downloads audio playlist using ytdlp with highest available quality.'), ('video_highest', 'Downloads single videos using ytdlp with highest available quality.'), ('video_playlist_highest', 'Downloads playlist using ytdlp with highest available quality.'), ('video_list_highest', 'Downloads videos from a list of URLs separated by newlines using ytdlp at the highest available quality.'), ('audio_list_highest', 'Downloads audios from a list of URLs separated by newlines using ytdlp at the highest available quality.')], default='video_highest', max_length=50),
        ),
    ]
