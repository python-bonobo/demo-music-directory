import functools
import itertools

import rdflib
from SPARQLWrapper import JSON

from mused.constants import PREFIXES


def with_sparql(sparql):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(sparql, *args, **kwargs)

        return wrapped

    return decorator


def to_term(x):
    if x['type'] == 'uri':
        return rdflib.URIRef(x['value'])
    elif x['type'] == 'literal':
        return rdflib.Literal(x['value'], lang=x.get('xml:lang', None))
    elif x['type'] == 'typed-literal':
        return rdflib.Literal(x['value'], datatype=x.get('datatype', None))
    else:
        raise ValueError('Conversion not implemented for {}.'.format(x['type']))


class Query:
    def __init__(self, select, *, where, suffix='LIMIT 10000', prefixes=None):
        self.select = select
        self.where = where
        self.suffix = suffix
        self.prefixes = prefixes or PREFIXES

    def __str__(self):
        return '\n'.join(
            itertools.chain(
                ('PREFIX {}: <{}>'.format(alias, url) for alias, url in sorted(self.prefixes.items())), (
                    'SELECT {}'.format(self.select),
                    'WHERE {{',
                    self.where,
                    '}}',
                    self.suffix,
                )
            )
        )

    def apply(self, sparql, *columns, **kwargs):
        query = self.format(**kwargs)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        row_filter = kwargs.pop('filter', None)
        for row in sorted(results["results"]["bindings"], key=lambda x: [x[c]['value'] for c in columns]):
            if row_filter and not row_filter(row):
                continue
            yield tuple(to_term(row[c]) for c in columns)

    def format(self, *args, **kwargs):
        return str(self).format(*args, **kwargs)
