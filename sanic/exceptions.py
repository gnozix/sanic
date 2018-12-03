from traceback import format_exc

from sanic.response import text
from sanic.log import log


class SanicException(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class InvalidUsage(SanicException):
    status_code = 400


class Headler:
    headlers = None
    def __init__(self, sanic):
        self.headlers = {}
        self.sanic = sanic

    def add(self, exception, handler):
        self.handlers[exception] = handler

    def response(self, request, exception):
        handler = self.handlers.get(type(exception), self.default)
        try:
            response = handler(
