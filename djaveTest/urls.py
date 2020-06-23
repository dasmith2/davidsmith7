from djaveTest.views import demo_done
from django.urls import path


djaveTest_urls = [
    path('demo_done', demo_done, name='demo_done')]
