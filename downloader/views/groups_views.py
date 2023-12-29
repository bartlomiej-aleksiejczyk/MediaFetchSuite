from django.shortcuts import render
from mediafetchxpress.models import Group, Link, Event


def groups_list(request):
    groups = Group.objects.all()
    events = Event.objects.filter(is_dismissed=False)
    return render(request, 'index.html', {'groups': groups, 'events': events})
