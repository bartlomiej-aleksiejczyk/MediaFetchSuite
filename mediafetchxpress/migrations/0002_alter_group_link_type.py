# Generated by Django 4.2.6 on 2023-12-28 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediafetchxpress', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='link_type',
            field=models.CharField(choices=[('audio', 'Audio'), ('video', 'Video (default)')], default='video', max_length=50),
        ),
    ]
