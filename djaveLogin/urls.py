from django.urls import path
from djaveLogin.views import login, logout


djave_login_urls = [
    path('login', login, name='djave_login'),
    path('login/<token>', login, name='djave_login'),
    path('logout', logout, name='djave_logout')]
