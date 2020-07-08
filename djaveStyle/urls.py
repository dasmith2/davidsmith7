from django.urls import path
from djaveStyle.views import css


djave_style_urls = [
    path('css/<template_file_name>', css, name='css')]
