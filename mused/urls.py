from django.urls import path

from mused.views import index, MusicGroupListView, MusicGroupDetailView, MusicGenreListView, \
    MusicGenreDetailView

urlpatterns = [
    path('', index, name='home'),
    path('groups', MusicGroupListView.as_view(), name='group_list'),
    path('groups/<slug:slug>', MusicGroupDetailView.as_view(), name='group_detail'),
    path('genres', MusicGenreListView.as_view(), name='genre_list'),
    path('genres/<slug:slug>', MusicGenreDetailView.as_view(), name='genre_detail'),
]
