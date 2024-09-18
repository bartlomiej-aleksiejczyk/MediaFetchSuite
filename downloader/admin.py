from django.contrib import admin
from .models import DownloadTask, TaskExecutionWindow

admin.site.register(TaskExecutionWindow)


@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    readonly_fields = ["priority"]
