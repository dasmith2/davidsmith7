from django.urls import path

from djavError.views import (
    see_error, js_error, errors, notifications, long_requests,
    too_many_queries, trigger_errors)


djaverror_urls = [
    path('js_error', js_error, name='js_error'),
    path('see_error/<pk>', see_error, name='see_error'),

    path('errors', errors, name='errors'),
    path('notifications', notifications, name='notifications'),
    path('long_requests', long_requests, name='long_requests'),
    path('too_many_queries', too_many_queries, name='too_many_queries'),
    path('trigger', trigger_errors, name='trigger_errors')]
