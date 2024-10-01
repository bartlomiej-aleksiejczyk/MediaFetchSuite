from django.urls import path
from iommi import Form, Table, Column
from .views import TaskListView, NewTaskView, delete_task, view_task

from .models import DownloadTask, TaskExecutionWindow

urlpatterns = [
    path("tasks/", TaskListView().as_view(), name="task_list"),
    path("tasks/<int:pk>/delete/", delete_task, name="delete_task"),
    path("tasks/<int:pk>/", view_task, name="view_task"),
    path(
        "tasks/new/",
        NewTaskView().as_view(),
    ),
    path(
        "time-windows/",
        Table(
            auto__model=TaskExecutionWindow,
        ).as_view(),
    ),
    path("time-windows/new/", Form.create(auto__model=TaskExecutionWindow).as_view()),
]
