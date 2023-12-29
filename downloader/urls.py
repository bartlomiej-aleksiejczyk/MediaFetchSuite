from django.urls import path
from downloader.views import groups_views, event_views, group_views, link_views
urlpatterns = [
    path('', groups_views.groups_list, name='index'),
    path('add_group/', group_views.add_group, name='add_group'),
    path('group/<int:group_id>/', group_views.group_details, name='group_details'),
    path('group/<int:group_id>/add_link/', link_views.add_link, name='add_link'),
    path('group/<int:group_id>/start_tasks/', group_views.start_group_tasks, name='start_group_tasks'),
    path('events/', event_views.events, name='events'),
]
# TODO: How to signal that group is set to be downloaded
# TODO: Make a chron job to download at night and stoppign downloading after noon (without stopping current download)
# TODO: What to do if group is downloaded and new the link is added to it
# TODO: Batch adding list of links
