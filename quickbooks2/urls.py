from django.urls import path

from quickbooks2.views import qb_authorize_callback


quickbooks2_urls = [
    path(
        'qb_authorize_callback', qb_authorize_callback,
        name='qb_authorize_callback')]
