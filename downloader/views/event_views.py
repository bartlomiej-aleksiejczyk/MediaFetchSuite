from django.shortcuts import render

from mediafetchxpress.models import Event


def events(request):
    all_events = Event.objects.filter(is_dismissed=False)
    return render(request, 'events/all_events.html', {'events': all_events})
