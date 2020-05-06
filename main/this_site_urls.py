from django.urls import include, path

from tracktime.urls import tracktime_urls
from biscuits.urls import biscuit_patterns


this_site_urls = [
    path('tt/', include(tracktime_urls)),
    path('b/', include(biscuit_patterns))]
