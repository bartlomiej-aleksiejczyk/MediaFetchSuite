# Generated by Django 5.0.6 on 2025-02-09 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0010_alter_downloadtask_save_strategy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadtask',
            name='save_strategy',
            field=models.CharField(choices=[('s3_save', 'Saves file to the s3 instance.'), ('LOCAL_FILESYSTEM_SAVE', 'Saves files to the local filesystem.')], default='LOCAL_FILESYSTEM_SAVE', max_length=50),
        ),
    ]
