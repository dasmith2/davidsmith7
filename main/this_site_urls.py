from django.urls import include, path

from invoice.urls import invoice_urls
from quickbooks2.urls import quickbooks2_urls
from tracktime.urls import tracktime_urls
from tracktime.views.homepage import homepage


this_site_urls = [
    path('', include(tracktime_urls)),
    path('invoice/', include(invoice_urls)),
    path('', homepage, name='tracktime_homepage'),
    path('', include(quickbooks2_urls))]
