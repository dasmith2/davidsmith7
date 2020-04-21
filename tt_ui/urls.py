from django.urls import path

from tt_ui.views import time_entry


tt_ui_urls = [
    path('tt', time_entry, name='time_entry')]
