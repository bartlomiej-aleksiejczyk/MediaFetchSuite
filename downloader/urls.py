from django.urls import path
from iommi import Form, Table, Column
from .views import TaskListView, NewTaskView

from .models import DownloadTask, TaskExecutionWindow

urlpatterns = [
    path(
        "tasks/",
        TaskListView().as_view(),
    ),
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
