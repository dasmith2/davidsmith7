from django.urls import path
from djaveLogin.views import (
    sign_up, login, logout, login_token, sign_up_email_preview)


djave_login_urls = [
    path('sign_up', sign_up, name='djave_sign_up'),
    path('sign_up/<token>', sign_up, name='djave_sign_up'),
    path('login', login, name='djave_login'),
    path('login/<token>', login, name='djave_login'),
    path('logout', logout, name='djave_logout'),

    path('login_token', login_token, name='login_token'),

    path(
        'sign_up_email_preview', sign_up_email_preview,
        name='sign_up_email_preview')]
