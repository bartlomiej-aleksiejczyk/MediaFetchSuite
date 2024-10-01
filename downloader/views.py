from django.shortcuts import render, redirect, get_object_or_404
from iommi import Form, Table, Column, Page, Action
from .models import DownloadTask, TaskExecutionWindow


class TaskListView(Page):
    new_task_button = Action(
        display_name="Create New Task",
        attrs__href="new/",
    )

    tasks_table = Table(
        auto__model=DownloadTask,
        columns__delete=Column.delete(),
    )


def delete_task(request, pk):
    task = get_object_or_404(DownloadTask, pk=pk)
    task.delete()
    return redirect("/download/tasks/")


def view_task(request, pk):
    task = get_object_or_404(DownloadTask, pk=pk)
    return "reree"


class NewTaskView(Page):
    go_back_button = Action(
        display_name="Go Back",
        attrs__href="/download/tasks/",
    )
    task_form = Form.create(
        auto__model=DownloadTask,
        auto__exclude=[
            "created_at",
            "updated_at",
            "priority",
            "error_message",
            "state",
        ],
    )
