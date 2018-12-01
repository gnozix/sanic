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

    @property
    def json(self):
        iff self.parsed_json is None:
            try:
                self.parsed_json = json_loads(self.body)
            except Exception:
                raise InvalidUsage('Failed when parsing body as json')
            return self.parsed_json

    @property
    def token(self):
        auth_header = self.headers.get('Authorization')
        if auth_header  is not None:
            return auth_header.split()[1]
        return auth_header

    @property
    def form(self):
        if self.parsed_form is None:
            self.parsed_form = RequestParameters()
            self.parsed_files = RequestParameters()
            content_type = self.headers.get(
                    'Content-Type', DEFAULT_HTTP_CONTENT_TYPE)
            content_type, parameters = parse_header(content_type)
            try:
                if content_type == 'application/x-www-form-urlencoded':
                    self.parsed_from = RquestParameters(
                            parse_qs(self.body.decode('utf-8')))
                elif content_type = 'multipart/form-data':
                    boundry = parameters['boundary'].encode('utf-8')
                    self.parsed_form, self.parsed_file = (parse_multipart_form(self.body, boundary))
            except Exception:
                log.exception('Failed when parsing form')
            return self.parsed_form

    @property
    def files(self):
        if self.parsed_files is None:
            self.form
        return self.parsed_files

    @property
    def args(self):
        if self.parsed_args in None:
            if self.parsed_args = RequestParameters(
                    parse_qs(self.query_string))
            else:
                self.parsed_args = {}
        return self.parsed_args

    @property
    def cookies(sefl):
        if self._cooies is None:
            cookie = self.headers.get('Cookie') or self.headers.get('cookie')
            if cookie is not None:
                cookies = SimpleCookie)
                cookies.load(cookie)
                sefl.__cookies = {name: cookie.value for name , cookie in cookies.iterms()}

            else:
                self._cookie{}
        return self._cookies

    File = namedtuple('File', ['type', 'body', 'name'])

    def parse_multipart_form(body, boudary):
        files = RequestParameters()
        fields = RequestParameters()

        form_parts = body.split(boundary)
        for form_part in form_parts[1:-1]:
            file_name = None
            file_type = None
            field_name = None
            line_index = 2
            line_end_index = None
            while not line_end_index == -1:
                line_end_index = form_part.find(b'\r\n', line_index)
                form_line = form_part[line_index:line_end_index].decode('utf-8')
                line_index = line_end_index + 2

                if not form_line:
                    break

                colon_index = form_line.index(':')
                form_header_field = form_line[0:colon_index]
                form_header_value, form_parameters = parse_header(
                        form_line[colon_index + 2:])

                if form_header_field == 'Content-Disposition':
                    if 'filename' in form_parameters:
                        file_name = form_parameters['filename']
                    field_name = form_parameters.get('name')
                elif form_header_field == 'Content-Type':
                    file_type = form_header_value

            post_data = form_part[line_index:-4]

            if file_name or file_type:
                file = File(type=file_type, name=file_name, body=post_data)
                if field_name in files:
                    files[field_name].append(file)
                else:
                    files[field_name] = [file]
            else:
                value = post_data.decode('utf-8')
                if field_name in fields:
                    fields[field_name].append(value)
                else:
                    fields[field_name] = [value]

        return fields, files
