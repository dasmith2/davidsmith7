from django.urls import include, path

from biscuits.urls import biscuit_patterns
from invoice.urls import invoice_urls
from tracktime.urls import tracktime_urls
from tracktime.views.homepage import homepage


this_site_urls = [
    path('tt/', include(tracktime_urls)),
    path('invoice/', include(invoice_urls)),
    path('b/', include(biscuit_patterns)),
    path('', homepage, name='tracktime_homepage')]
