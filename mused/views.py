from django.db.models import Count
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from mused.models import MusicGroup, MusicGenre
from mused.paginator import Paginator


def index(request):
    return render(request, 'mused/index.html', {'current': 'home'})


class MusicGroupViewMixin:
    model = MusicGroup


class MusicGenreViewMixin:
    model = MusicGenre


class MusicGroupListView(MusicGroupViewMixin, ListView):
    template_name = 'mused/group_list.html'
    paginate_by = 20
    paginator_class = Paginator

    def get_queryset(self):
        queryset = super(MusicGroupListView, self).get_queryset()

        musicgenre_id = self.kwargs.get('musicgenre_id', None)
        if musicgenre_id:
            queryset = queryset.filter(genres__id=musicgenre_id)

        limit = self.kwargs.get('limit', None)
        if limit:
            queryset = queryset[:limit]

        return queryset


class MusicGroupDetailView(MusicGroupViewMixin, DetailView):
    template_name = 'mused/group_detail.html'


class MusicGenreListView(MusicGenreViewMixin, ListView):
    template_name = 'mused/genre_list.html'
    paginate_by = 20
    paginator_class = Paginator

    def get_queryset(self):
        queryset = super(MusicGenreListView, self).get_queryset()

        musicgroup_id = self.kwargs.get('musicgroup_id', None)
        if musicgroup_id:
            queryset = queryset.filter(groups__id=musicgroup_id)

        queryset = queryset.annotate(groups_count=Count('groups')).filter(groups_count__gt=0)

        limit = self.kwargs.get('limit', None)
        if limit:
            queryset = queryset[:limit]

        return queryset


class MusicGenreDetailView(MusicGenreViewMixin, DetailView):
    template_name = 'mused/genre_detail.html'
