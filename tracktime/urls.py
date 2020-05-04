from django.urls import path

from tracktime.views import (
    enter_time, add_up_time, delete_tracked, to_do, to_do_done, delete_to_do)


tracktime_urls = [
    path('', enter_time, name='enter_time'),
    path('aggregate', add_up_time, name='add_up_time'),
    path('to_do', to_do, name='to_do'),

    path('delete_tracked', delete_tracked, name='delete_tracked'),
    path('to_do_done', to_do_done, name='to_do_done'),
    path('delete_to_do', delete_to_do, name='delete_to_do')]
