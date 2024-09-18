# Generated by Django 5.0.6 on 2024-09-18 18:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('downloader', '0003_alter_downloadtask_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadtask',
            name='catalogue_name',
            field=models.CharField(blank=True, help_text='Only letters, numbers, underscores, and hyphens are allowed.', max_length=255, validators=[django.core.validators.RegexValidator(message='Only letters, numbers, dots, underscores, and hyphens are allowed.', regex='^[a-z0-9_-]*$')]),
        ),
    ]
