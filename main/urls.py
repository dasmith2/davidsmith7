from django.conf import settings
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.urls import include, path
from djavError.urls import djaverror_urls

from example.urls import example_urls
from tracktime.urls import tracktime_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(auth_urls)),
    path('', include(djaverror_urls)),
    path('tt/', include(tracktime_urls))
]

if settings.DEBUG:
  import debug_toolbar
  urlpatterns += [path('', include(debug_toolbar.urls))]
