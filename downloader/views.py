import os

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from .models import DownloadTask, TaskExecutionWindow

LOG_FILE_PATH = 'logs/download-progress.log'

# ✅ Task List View (With Pagination)
class TaskListView(ListView):
    model = DownloadTask
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10  # Show 10 tasks per page
    ordering = ['-id']


# ✅ Task Detail View
class TaskDetailView(DetailView):
    model = DownloadTask
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


# ✅ Task Creation View
class TaskCreateView(CreateView):
    model = DownloadTask
    template_name = "tasks/new_task.html"
    fields = [
        "urls",
        "download_strategy",
        "save_strategy",
        "catalogue_name",
    ]
    success_url = reverse_lazy("downloader:task_list")


# ✅ Task Delete View
class TaskDeleteView(DeleteView):
    model = DownloadTask
    template_name = "tasks/delete_task.html"
    success_url = reverse_lazy("downloader:task_list")


# ✅ Execution Window List View (With Pagination)
class ExecutionWindowListView(ListView):
    model = TaskExecutionWindow
    template_name = "tasks/time_windows_list.html"
    context_object_name = "windows"
    paginate_by = 10  # Show 10 execution windows per page


class ExecutionWindowCreateView(CreateView):
    model = TaskExecutionWindow
    template_name = "tasks/new_execution_window.html"  # This template must exist
    fields = ["start_time", "end_time"]
    success_url = reverse_lazy("downloader:time_windows_list")

def log_view(request):
    logs = []
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()[-500:]  # Read last 50 log lines

    return render(request, 'tasks/logs.html', {'logs': logs})