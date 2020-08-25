from django.urls import path

from biscuits.views import (
    private_biscuits, public_biscuits, view_private_biscuit)


biscuit_patterns = [
    path('', public_biscuits, name='public_biscuits'),
    path('private_biscuits', private_biscuits, name='private_biscuits'),
    path(
        'view_private_biscuit/<file_name>', view_private_biscuit,
        name='view_private_biscuit')]
