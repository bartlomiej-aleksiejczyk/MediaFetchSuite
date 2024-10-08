# Generated by Django 5.0.6 on 2024-09-17 11:20

import downloader.domain.task_state
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadtask',
            name='priority',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='downloadtask',
            name='state',
            field=models.CharField(choices=downloader.domain.task_state.TaskState.choices, default=downloader.domain.task_state.TaskState['PENDING'], max_length=20),
        ),
    ]
