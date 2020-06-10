from django.urls import include, path

from biscuits.urls import biscuit_patterns
from tracktime.urls import tracktime_urls


this_site_urls = [
    path('tt/', include(tracktime_urls)),
    path('b/', include(biscuit_patterns))]
