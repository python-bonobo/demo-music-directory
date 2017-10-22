from SPARQLWrapper import SPARQLWrapper

import bonobo
from bonobo.config import use
from bonobo.ext.django import ETLCommand
from mused.utils.sparql import Query


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


class Command(ETLCommand):
    @use('dbpedia')
    def extract_genres(self, dbpedia):
        yield from AllGenresQuery().apply(dbpedia, 'genre', 'count')

    def load(self, genre, count):
        self.stdout.write(f'{genre} {count}')

    def get_graph(self, *args, **options):
        return bonobo.Graph(
            self.extract_genres,
            self.load,
        )

    def get_services(self):
        return {
            'dbpedia': SPARQLWrapper('http://de.dbpedia.org/sparql'),
        }
