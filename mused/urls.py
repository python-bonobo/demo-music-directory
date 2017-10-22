from django.urls import path

from mused.views import index, MusicGroupListView, MusicGroupDetailView

urlpatterns = [
    path('', index, name='home'),
    path('groups', MusicGroupListView.as_view(), name='group_list'),
    path('groups/<slug:slug>', MusicGroupDetailView.as_view(), name='group_detail'),
]
