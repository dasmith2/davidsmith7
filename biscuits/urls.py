from django.urls import path

from biscuits.views import private_biscuits, public_biscuits


biscuit_patterns = [
    path('', public_biscuits, name='public_biscuits'),
    path('private_biscuits', private_biscuits, name='private_biscuits')]
