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


_LegalChars = string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~:"
_is_legal_key = re.compile('[%s]+' % re.escape(_LegalChars)).fullmatch
_UnescapedChars = _LegalChars + ' ()/<=>?@[]{}'

_Translator = {n: '\\%03o' % n
                       for n in set(range(256)) - set(map(ord, _UnescapedChars))}
_Translator.update({
    ord('"'): '\\"',
    ord('\\'): '\\\\',
})


def _quote(str_data):
    if str_data is None or _is_legal_key(str_data):
        return str_data
    else:
        return '"' + str_data.translate(_Translator) + '"'


class Cookie(dict):
    _keys = {
        "expires": "expires",
        "path": "Path",
        "comment": "Comment",
        "domain": "Domain",
        "max-age": "Max-Age",
        "secure": "Secure",
        "httponly": "HttpOnly",
        "version": "Version",
    }
    _flags = {'secure', 'httponly'}

    def __init__(self, key, value):
        if key in self._keys:
            raise KeyError('Cookie name is a reserved word')
        if not _is_legal_key(key):
            raise KeyError('Cookie key contains illegal characters')
        self.key = key
        self.value = value
        super().__init__()

    def __setitem__(self, key, value):
        if key not in self._keys:
            raise KeyError('Unknown cookie property')
        return super().__setitem__(key, value)

    def encode(self, encoding):
        output = ['{}={}'.format(self.key, _quote(self.value))]
        for key, value in self.items():
            if key == 'max-age' and isinstance(value, int):
                output.append('{}={}'.format(self._keys[key], value))
            elif key == 'expires' and isinstance(value, datetime):
                output.append('{}={}'.format(
                    self._keys[key],
                    value.strftime('%a, %d-%b-%Y %T GMT')
                ))
            elif key in self._flage:
                output.append(self._keys[key])
            else:
                output.append('{}={}'.format(self._keys[key], value))
        return '; '.join(output).encode(encoding)

