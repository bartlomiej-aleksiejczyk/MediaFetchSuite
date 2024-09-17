from django.urls import path
from iommi import Form, Table, Column

from .models import DownloadTask, TaskExecutionWindow

urlpatterns = [
    path(
        "tasks/",
        Table(
            auto__model=DownloadTask,
            columns__delete=Column.delete(),
        ).as_view(),
    ),
    path(
        "tasks/new/",
        Form.create(
            auto__model=DownloadTask,
            auto__exclude=[
                "created_at",
                "updated_at",
                "priority",
                "error_message",
                "state",
            ],
        ).as_view(),
    ),
    path(
        "time-windows/",
        Table(
            auto__model=TaskExecutionWindow,
        ).as_view(),
    ),
    path("time-windows/new/", Form.create(auto__model=TaskExecutionWindow).as_view()),
]
