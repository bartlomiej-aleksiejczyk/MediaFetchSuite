from django.shortcuts import render, redirect
from django.urls import reverse
from mediafetchxpress.models import Group, Link, Event


def add_link(request, group_id):
    if request.method == 'POST':
        url = request.POST.get('url')
        Link.objects.create(url=url, group_id=group_id)
        return redirect(reverse('group_details', args=[group_id]))
    return render(request, 'links/add_link.html', {'group_id': group_id})
