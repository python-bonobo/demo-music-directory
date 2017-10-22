from django.shortcuts import render
from django.views.generic import ListView, DetailView

from mused.models import MusicGroup, MusicGenre
from mused.paginator import Paginator


def index(request):
    return render(request, 'mused/index.html', {'current': 'home'})


class MusicGroupListView(ListView):
    template_name = 'mused/group_list.html'
    model = MusicGroup
    paginate_by = 20
    paginator_class = Paginator


class MusicGroupDetailView(DetailView):
    template_name = 'mused/group_detail.html'
    model = MusicGroup


class MusicGenreListView(ListView):
    template_name = 'mused/genre_list.html'
    model = MusicGenre
    paginate_by = 20
    paginator_class = Paginator


class MusicGenreDetailView(DetailView):
    template_name = 'mused/genre_detail.html'
    model = MusicGenre
