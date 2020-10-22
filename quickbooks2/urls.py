from django.urls import path

from quickbooks2.views.auth import (
    qb_authorize_callback, show_authorization_url,
    post_quickbooks_authorization)
from quickbooks2.views.browse import (
    quickbooks2_model_list, quickbooks2_model_instance)


quickbooks2_urls = [
    path(
        'qb_authorize_callback', qb_authorize_callback,
        name='qb_authorize_callback'),
    path(
        'show_authorization_url', show_authorization_url,
        name='show_authorization_url'),
    path(
        'post_quickbooks_authorization', post_quickbooks_authorization,
        name='post_quickbooks_authorization'),
    path(
        'quickbooks/<model_name>', quickbooks2_model_list,
        name='quickbooks2_model_list'),
    path(
        'quickbooks/<model_name>/view/<pk>', quickbooks2_model_instance,
        name='quickbooks2_model_instance')]
