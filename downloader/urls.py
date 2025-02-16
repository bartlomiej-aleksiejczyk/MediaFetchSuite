from django.urls import path
from .views import (
    TaskListView,
    TaskDetailView,
    TaskCreateView,
    TaskDeleteView,
    ExecutionWindowListView,
    ExecutionWindowCreateView,
    log_view
)

app_name = 'downloader'

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/new/", TaskCreateView.as_view(), name="new_task"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="delete_task"),

    path("time-windows/", ExecutionWindowListView.as_view(), name="time_windows_list"),
    path("time-windows/new/", ExecutionWindowCreateView.as_view(), name="new_time_window"),
    path("tasks/logs", log_view, name="task_logs"),

]
