from tracktime.urls import tracktime_urls

this_site_urls = [
    path('tt/', include(tracktime_urls))]
