from django.urls import path

from quickbooks2.views.auth import (
    qb_authorize_callback, show_authorization_url,
    post_quickbooks_authorization)
from quickbooks2.views.browse import qb2_customers, qb2_customer


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
        'quickbooks/customers', qb2_customers, name='qb2_customers'),
    path(
        'quickbooks/customer/<pk>', qb2_customer, name='qb2_customer')]
