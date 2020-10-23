from django.urls import path

from quickbooks2.views.auth import (qb_authorize_callback, auth_stuff)
from quickbooks2.views.browse import (
    quickbooks2_model_list, quickbooks2_model_instance)


quickbooks2_urls = [
    path(
        'qb_authorize_callback', qb_authorize_callback,
        name='qb_authorize_callback'),
    path('quickbooks/auth_stuff', auth_stuff, name='auth_stuff'),
    path(
        'quickbooks/<model_name>', quickbooks2_model_list,
        name='quickbooks2_model_list'),
    path(
        'quickbooks/<model_name>/view/<pk>', quickbooks2_model_instance,
        name='quickbooks2_model_instance')]
