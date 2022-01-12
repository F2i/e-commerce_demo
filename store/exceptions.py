from django.http.response import HttpResponse
from django.shortcuts import redirect

class PermissonDeniedException(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    def render(self):
        return HttpResponse('hello')