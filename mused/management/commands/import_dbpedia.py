import rdflib
import requests
import requests_cache

import bonobo
from bonobo import Bag
from bonobo.config import use, ContextProcessor, Configurable
from bonobo.constants import NOT_MODIFIED
from bonobo.ext.django import ETLCommand
from bonobo.util import ValueHolder
from mused.models import MusicGroup, MusicGenre
from mused.utils.sparql import RequestsSPARQLWrapper, Query


class AllGenresQuery(Query):
    def __init__(self, min_count=100):
        super().__init__(
            'DISTINCT ?genre, COUNT(*) as ?count',
            where='?item dbo:genre ?genre.',
            suffix='''
                GROUP BY ?genre HAVING (COUNT(?genre) >= {})
                ORDER BY DESC(?count)
                LIMIT 10000
            '''.format(min_count)
        )


class MusicGroupsByGenreQuery(Query):
    def __init__(self):
        super().__init__('DISTINCT ?subject', where='?subject a schema:MusicGroup ; dbo:genre <{genre}>')


class GroupByMusicGroups(Configurable):
    @ContextProcessor
    def grouped_genres(self, context):
        grouped = yield ValueHolder({})
        for musicgroup_id, genres in grouped.get().items():
            context.send(Bag(musicgroup_id, genres=genres))

    def call(self, grouped_genres, genre, musicgroup):
        musicgroup_id = str(musicgroup)
        if not musicgroup_id in grouped_genres:
            grouped_genres[musicgroup_id] = set()
        grouped_genres[musicgroup_id].add(str(genre))


class Command(ETLCommand):
    @use('dbpedia')
    def extract_genres(self, dbpedia):
        yield from AllGenresQuery().apply(dbpedia, 'genre')

    @use('dbpedia')
    def join_musicgroups(self, dbpedia, genre):
        for (subject, ) in MusicGroupsByGenreQuery().apply(dbpedia, 'subject', genre=genre):
            yield genre, subject

    group_by_musicgroups = GroupByMusicGroups()

    @use('dbpedia')
    def get_musicgroup_attributes(self, dbpedia, subject, **kwargs):
        attributes = {}
        query = Query('*', where='<{subject}> ?p ?o FILTER (langMatches(lang(?o), "de"))')
        for v, o in query.apply(dbpedia, 'p', 'o', subject=subject):
            if v == rdflib.RDFS.label:
                if not 'title' in attributes:
                    attributes['title'] = str(o)
            elif v == rdflib.RDFS.comment:
                if not 'description' in attributes:
                    attributes['description'] = str(o)
        yield subject, {**kwargs, **attributes}

    def create_or_update_musicgroup(self, subject, *, genres, **attributes):
        obj, created, updated = self.create_or_update(MusicGroup, subject=subject, defaults=attributes)

        obj.genres.add(*(MusicGenre.objects.get_or_create(subject=subject)[0] for subject in genres))

        yield NOT_MODIFIED

    @use('dbpedia')
    def get_genre_attributes(self, dbpedia, subject):
        attributes = {}
        query = Query('*', where='<{subject}> ?p ?o FILTER (langMatches(lang(?o), "de"))')
        for v, o in query.apply(dbpedia, 'p', 'o', subject=subject):
            if v == rdflib.RDFS.label:
                if not 'title' in attributes:
                    attributes['title'] = str(o)
            elif v == rdflib.RDFS.comment:
                if not 'description' in attributes:
                    attributes['description'] = str(o)

        yield subject, attributes

    def create_or_update_musicgenre(self, subject, **attributes):
        obj, created, updated = self.create_or_update(MusicGenre, subject=subject, defaults=attributes)
        yield NOT_MODIFIED

    def get_graph(self, *args, **options):
        graph = bonobo.Graph()

        graph.add_chain(
            self.extract_genres,
            self.join_musicgroups,
            self.group_by_musicgroups,
            self.get_musicgroup_attributes,
            self.create_or_update_musicgroup,
        )

        graph.add_chain(
            self.get_genre_attributes,
            self.create_or_update_musicgenre,
            _input=self.extract_genres,
        )

        return graph

    def get_services(self):
        requests_cache.install_cache('http_cache')
        http = requests.Session()
        return {
            'dbpedia': RequestsSPARQLWrapper('http://de.dbpedia.org/sparql', http=http),
            'http': http,
        }
