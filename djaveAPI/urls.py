from django.urls import path

from djaveAPI.views.ajax import ajax_update, ajax_delete
from djaveAPI.views.api import list_or_save_new, get_or_save_existing
from djaveAPI.views.keys import delete_key, user_api_keys


djave_api_urls = [
    path('delete_key', delete_key, name='delete_key'),

    path('user_api_keys', user_api_keys, name='user_api_keys'),

    path('ajax_update', ajax_update, name='ajax_update'),
    path('ajax_delete', ajax_delete, name='ajax_delete'),

    # These patterns capture quite a lot so they have to come last. They're for
    # the API.
    path('<model_name>', list_or_save_new, name='list_or_save_new'),
    path(
        '<model_name>/<pk>', get_or_save_existing,
        name='get_or_save_existing')]
