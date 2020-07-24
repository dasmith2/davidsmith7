from django.urls import path

from djavError.views import (
    see_error, js_error, errors, notifications, long_requests,
    too_many_queries, trigger_errors, all_fixed)


handler404 = 'djavError.views.handler404'
handler500 = 'djavError.views.handler500'


djaverror_urls = [
    path('js_error', js_error, name='js_error'),
    path('see_error/<pk>', see_error, name='see_error'),

    path('errors', errors, name='errors'),
    path('notifications', notifications, name='notifications'),
    path('long_requests', long_requests, name='long_requests'),
    path('too_many_queries', too_many_queries, name='too_many_queries'),
    path('trigger', trigger_errors, name='trigger_errors'),
    path('all_fixed/<model_name>/<pks>', all_fixed, name='all_fixed')]
