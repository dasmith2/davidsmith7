from django.urls import path

from djaveAPI.views import list_objects, get_object, delete_key, user_api_keys


djave_api_urls = [
    path('delete_key', delete_key, name='delete_key'),

    path('user_api_keys', user_api_keys, name='user_api_keys'),

    # These patterns capture quite a lot so they have to come last.
    path('<model_name>', list_objects, name='list_objects'),
    path('<model_name>/<pk>', get_object, name='get_object')]
