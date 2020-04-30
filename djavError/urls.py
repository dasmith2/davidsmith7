from django.urls import path

from djavError.views import js_error, see_error


djaverror_urls = [
    path('js_error', js_error, name='js_error'),
    path('admin/errors/error/<pk>/change/', see_error, name='see_error')]
