from cgi import parse_header
from collections import namedtuple
from http.cookies import SimpleCookie
from httptools import parse_url
from urllib.parse import parse_qs
from ujson import loads as json_loads

from sanic.exceptions import InvalidUsage
from sanic.log import log


DEFAULT_HTTP_CONTENT_TYPE = 'application/octet-stream'


class RequestParameters(dict):
    def get(self, name, default=None):
        return super().get(name, [default])[0]

    def getlist(self, name, default=None):
        return super().get(name, default)


class Request(dict):
    __slots__ = (
            'url', 'headers', 'version', 'method', '_cookies',
            'query_string', 'body', 'parsed_json',
            'parsed_args', 'parsed_form', 'parsed_files',
            )

    def __init__(self, url_bytes, headers, version, method):
        url_parsed = parse_url(url_bytes)
        self.url = url_parsed.path.decode('utf-8')
        self.headers = headers
        self.version = version
        self.method = method
        self.query_string = None
        if url_parsed.query:
            self.query_string = url_parsed.query.decode('utf-8')

        self.body = None
        self.parsed_json = None
        self.parsed_form = None
        self.parsed_files = None
        self.parsed_args = None
        self._cookies = None

