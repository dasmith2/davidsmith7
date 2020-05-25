from django.urls import path

from djaveAPI.views import list_objects, get_object


djave_api_urls = [
    path('<model_name>', list_objects, name='list_objects'),
    path('<model_name>/<pk>', get_object, name='get_object')]
