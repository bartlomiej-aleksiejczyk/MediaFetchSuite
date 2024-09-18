from django.db import transaction
from django.db.models import F, Max
from django.apps import apps


from django.apps import apps
from django.db import transaction


@transaction.atomic
def reorder_task_priorities_after_unset():
    print("apud")
    DownloadTask = apps.get_model("downloader", "DownloadTask")

    tasks = DownloadTask.objects.all().order_by("priority")

    updated_tasks = []

    for index, task in enumerate(tasks):
        new_priority = index + 1
        if task.priority != new_priority:
            task.priority = new_priority
            updated_tasks.append(task)

    if updated_tasks:
        DownloadTask.objects.bulk_update(updated_tasks, ["priority"])


@transaction.atomic
def reorder_priorities_to_updated_task(new_task):
    DownloadTask = apps.get_model("downloader", "DownloadTask")

    MIN_PRIORITY = 1

    max_priority = (
        DownloadTask.objects.aggregate(max_priority=Max("priority"))["max_priority"]
        or 0
    )

    if new_task.priority < MIN_PRIORITY:
        new_task.priority = MIN_PRIORITY
    elif new_task.priority >= max_priority:
        new_task.priority = max_priority + 1

    if (
        DownloadTask.objects.filter(priority=new_task.priority)
        .exclude(id=new_task.id)
        .exists()
    ):
        tasks_to_update = DownloadTask.objects.filter(
            priority__gte=new_task.priority
        ).exclude(id=new_task.id)

        tasks_to_update.update(priority=F("priority") + 1)
