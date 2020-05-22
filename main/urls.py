""" These urls apply to all sites. Put site-specific stuff in
main/this_site_urls.py """
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.urls import include, path
from djavError.urls import djaverror_urls
from djaveLogin.urls import djave_login_urls
from djaveS3.urls import djave_s3_urls

from main.views import all_sites_js, this_site_js, all_sites_css, this_site_css
from main.this_site_urls import this_site_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(auth_urls)),
    path('js/all_sites.js', all_sites_js, name='all_sites_js'),
    path('js/this_site.js', this_site_js, name='this_site_js'),
    path('css/all_sites.css', all_sites_css, name='all_sites_css'),
    path('css/this_site.css', this_site_css, name='this_site_css'),
    path('', include(djave_login_urls)),
    path('', include(djaverror_urls)),
    path('', include(djave_s3_urls)),
    path('', include(this_site_urls))
]

if settings.DEBUG:
  import debug_toolbar
  urlpatterns += [path('', include(debug_toolbar.urls))]
