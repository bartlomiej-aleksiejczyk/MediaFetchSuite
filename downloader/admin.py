from django.contrib import admin
from .models import DownloadTask, TaskExecutionWindow

admin.site.register(DownloadTask)
admin.site.register(TaskExecutionWindow)
