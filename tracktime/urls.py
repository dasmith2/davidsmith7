from django.urls import path

from tracktime.views import (
    enter_time, add_up_time, time_list, delete_tracked)


tracktime_urls = [
    path('', enter_time, name='enter_time'),
    path('aggregate', add_up_time, name='add_up_time'),
    path('list', time_list, name='time_list'),

    path('delete_tracked', delete_tracked, name='delete_tracked')]
