from django.urls import path

from djavError.views.see_error import see_error
from djavError.views.js_error import js_error

from djavError.views.errors import errors
from djavError.views.notifications import notifications
from djavError.views.long_requests import long_requests
from djavError.views.too_many_queries import too_many_queries


djaverror_urls = [
    path('js_error', js_error, name='js_error'),
    path('see_error/<pk>', see_error, name='see_error'),

    path('errors', errors, name='errors'),
    path('notifications', notifications, name='notifications'),
    path('long_requests', long_requests, name='long_requests'),
    path('too_many_queries', too_many_queries, name='too_many_queries')]
