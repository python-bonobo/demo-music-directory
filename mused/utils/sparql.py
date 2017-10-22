import functools
import itertools
import re
import socket
import urllib.parse
import warnings

import rdflib
import requests
from SPARQLWrapper import SPARQLWrapper as BaseSPARQLWrapper, POST
from SPARQLWrapper.KeyCaseInsensitiveDict import KeyCaseInsensitiveDict
from SPARQLWrapper.Wrapper import QueryResult, _SPARQL_XML, XML, _SPARQL_JSON, JSON, _RDF_XML, RDF, _RDF_N3, TURTLE, N3, \
    _RDF_JSONLD, JSONLD, _returnFormatSetting

from mused.constants import PREFIXES


def normalize_sparql_query(q):
    return re.sub('\s+', ' ', q).strip()


class RequestsSPARQLWrapper(BaseSPARQLWrapper):
    def __init__(self, *args, **kwargs):
        http = kwargs.pop('http', None)
        super().__init__(*args, **kwargs)
        self._http = http or requests

    def _createRequest(self):
        """Internal method to create request according a HTTP method. Returns a
        C{urllib2.Request} object of the urllib2 Python library
        @return: request
        """
        request = None

        if self.isSparqlUpdateRequest():
            raise NotImplementedError('no, sorry.')
        else:
            if self.method == POST:
                raise NotImplementedError('no, sorry.')
            else:
                url = self.endpoint + "?" + self._getRequestEncodedParameters(("query", self.queryString))
                request = requests.Request('GET', url)

        request.headers['User-Agent'] = self.agent
        request.headers['Accept'] = self._getAcceptHeader()

        if self.user and self.passwd:
            raise NotImplementedError('no, sorry.')

        return request.prepare()

    def _query(self):
        """Internal method to execute the query. Returns the output of the
        C{urllib2.urlopen} method of the standard Python library

        @return: tuples with the raw request plus the expected format
        """
        if self.timeout:
            socket.setdefaulttimeout(self.timeout)

        request = self._createRequest()

        try:
            response = self._http.send(request)
            return response, self.returnFormat
        except Exception:  # implement?
            raise

    def query(self):
        return RequestsQueryResult(self._query())

    def _getRequestEncodedParameters(self, query=None):
        # Note
        # ----
        # This method has been overwritten to generate query string in the same order everytime, so the responses are
        # cacheable for sure.

        query_parameters = self.parameters.copy()

        if query and type(query) == tuple and len(query) == 2:
            query_parameters[query[0]] = [query[1]]

        for f in _returnFormatSetting:
            query_parameters[f] = [self.returnFormat]

        pairs = (
            "%s=%s" % (
                urllib.parse.quote_plus(param.encode('UTF-8'), safe='/'),
                urllib.parse.quote_plus(value.encode('UTF-8'), safe='/')
            ) for param, values in sorted(query_parameters.items()) for value in values
        )

        return '&'.join(pairs)

    def setQuery(self, query):
        return super().setQuery(normalize_sparql_query(query))


class RequestsQueryResult(QueryResult):
    def info(self):
        return KeyCaseInsensitiveDict(self.response.headers)

    def _convertJSON(self):
        return self.response.json()

    def _convertXML(self):
        raise NotImplementedError('XML conversion not implemented.')

    def _convertJSONLD(self):
        raise NotImplementedError('JSONLD conversion not implemented.')

    def _convertRDF(self):
        raise NotImplementedError('RDF conversion not implemented.')

    def _convertN3(self):
        raise NotImplementedError('N3 conversion not implemented.')

    def convert(self):
        """
        Encode the return value depending on the return format:
            - in the case of XML, a DOM top element is returned;
            - in the case of JSON, a simplejson conversion will return a dictionary;
            - in the case of RDF/XML, the value is converted via RDFLib into a Graph instance.
        In all other cases the input simply returned.

        @return: the converted query result. See the conversion methods for more details.
        """

        def _content_type_in_list(real, expected):
            return True in [real.find(mime) != -1 for mime in expected]

        def _validate_format(format_name, allowed, mime, requested):
            if requested not in allowed:
                message = "Format requested was %s, but %s (%s) has been returned by the endpoint"
                warnings.warn(message % (requested.upper(), format_name, mime), RuntimeWarning)

        if "content-type" in self.info():
            ct = self.info()["content-type"]

            if _content_type_in_list(ct, _SPARQL_XML):
                _validate_format("XML", [XML], ct, self.requestedFormat)
                return self._convertXML()
            elif _content_type_in_list(ct, _SPARQL_JSON):
                _validate_format("JSON", [JSON], ct, self.requestedFormat)
                return self._convertJSON()
            elif _content_type_in_list(ct, _RDF_XML):
                _validate_format("RDF/XML", [RDF, XML], ct, self.requestedFormat)
                return self._convertRDF()
            elif _content_type_in_list(ct, _RDF_N3):
                _validate_format("N3", [N3, TURTLE], ct, self.requestedFormat)
                return self._convertN3()
            elif _content_type_in_list(ct, _RDF_JSONLD):
                _validate_format("JSON(-LD)", [JSONLD, JSON], ct, self.requestedFormat)
                return self._convertJSONLD()

        raise RuntimeError('Unknown response content type {}.'.format(self.info()["content-type"]))


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
            itertools.chain(('PREFIX {}: <{}>'.format(alias, url) for alias, url in sorted(self.prefixes.items())), (
                'SELECT {}'.format(self.select),
                'WHERE {{',
                self.where,
                '}}',
                self.suffix,
            ))
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
