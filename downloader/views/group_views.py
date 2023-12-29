from django.shortcuts import render, redirect
from django.urls import reverse

from downloader.forms.group_form import GroupForm
from downloader.utils.link_type_strategies_handler import get_strategy
from mediafetchxpress.models import Group, Link, Event


def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = GroupForm()

    return render(request, 'group/add_group.html', {'form': form})


def group_details(request, group_id):
    group = Group.objects.get(id=group_id)
    links = group.link_set.all()
    return render(request, 'group/group_details.html', {'group': group, 'links': links})


def start_group_tasks(request, group_id):
    group = Group.objects.get(id=group_id)
    links = Link.objects.filter(group_id=group_id)
    strategy = get_strategy(group.link_type)
    for link in links:
        strategy.process_link(link.id)
    return redirect(reverse('group_details', args=[group_id]))
