from django.urls import path
from djaveLogin.views import login, logout, login_token


djave_login_urls = [
    path('login', login, name='djave_login'),
    path('login/<token>', login, name='djave_login'),
    path('logout', logout, name='djave_logout'),

    path('login_token', login_token, name='login_token')]
