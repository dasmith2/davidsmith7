from django.urls import path

from djaveAPI.views.api import (
    list_or_save_new, get_save_or_delete_existing, api_root)


djave_api_urls = [
    # These patterns capture quite a lot so they have to come last.
    path('', api_root, name='api_root'),
    path('<model_name>', list_or_save_new, name='list_or_save_new'),
    path(
        '<model_name>/<pk>', get_save_or_delete_existing,
        name='get_save_or_delete_existing')]
