from datetime import datetime
import re
import string

class CookieJar(dict):
    def __init__(self, headers):
        super().__init__()
        self.headers = headers
        self.cookie_headers = {}

    def __setitem__(self, key, value):
        cookie_header = self.cookie_headers.get(key)
        if not cookie_header:
            cookie = Cookie(key, value)
            cookie_header = MultiHeader('Set-Cookie')
            self.cookie_headers[key] = cookie_header
            self.headers[cookie_header] = cookie
            return super().__setitem__(key, cookie)
        else:
            self[key].value = value

    def __delitem__(self, key):
        del self.cookie_headers[key]
        return super().__delitem__(key)


class MultiHeader:
    def __init__(self, name):
        self.name = name

    def encode(self):
        return self.name.encode()

