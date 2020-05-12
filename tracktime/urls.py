from django.urls import path

from tracktime.views import (
    enter_time, delete_tracked, to_do, to_do_done, delete_to_do,
    edit_description, to_do_for_another_project)


tracktime_urls = [
    path('', enter_time, name='enter_time'),
    path('to_do', to_do, name='to_do'),

    path('delete_tracked', delete_tracked, name='delete_tracked'),
    path('to_do_done', to_do_done, name='to_do_done'),
    path('delete_to_do', delete_to_do, name='delete_to_do'),
    path('edit_description', edit_description, name='edit_description'),
    path(
        'to_do_for_another_project', to_do_for_another_project,
        name='to_do_for_another_project')]
