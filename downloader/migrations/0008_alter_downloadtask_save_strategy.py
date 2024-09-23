# Generated by Django 5.0.6 on 2024-09-23 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0007_remove_downloadtask_url_downloadtask_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadtask',
            name='save_strategy',
            field=models.CharField(choices=[('s3_save', 'Saves file to the s3 instance.'), ('LOCAL_FILESYSTEM_SAVE', 'Saves files to the local filesystem.')], default='LOCAL_FILESYSTEM_SAVE', max_length=50),
        ),
    ]
