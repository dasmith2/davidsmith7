from django.urls import path

from djaveAPI.views import (
    list_or_save_new, get_or_save_existing, delete_key, user_api_keys,
    update_webhook_url)


djave_api_urls = [
    path('delete_key', delete_key, name='delete_key'),
    path('update_webhook_url', update_webhook_url, name='update_webhook_url'),

    path('user_api_keys', user_api_keys, name='user_api_keys'),

    # These patterns capture quite a lot so they have to come last.
    path('<model_name>', list_or_save_new, name='list_or_save_new'),
    path(
        '<model_name>/<pk>', get_or_save_existing,
        name='get_or_save_existing')]
