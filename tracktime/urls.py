from django.urls import path

from tracktime.views import (
    enter_time, delete_work_session, to_do, to_do_done, delete_to_do,
    edit_description, to_do_for_another_project, report, project_work_report,
    projects, archived_projects, archive_project, unarchive_project,
    rename_project, api_docs, settings)


tracktime_urls = [
    path('', enter_time, name='enter_time'),
    path('to_do', to_do, name='to_do'),
    path(
        'to_do_for_another_project', to_do_for_another_project,
        name='to_do_for_another_project'),
    path('report', report, name='report'),
    path(
        'project_work_report', project_work_report,
        name='project_work_report'),

    path(
        'delete_work_session', delete_work_session,
        name='delete_work_session'),
    path('to_do_done', to_do_done, name='to_do_done'),
    path('delete_to_do', delete_to_do, name='delete_to_do'),
    path('edit_description', edit_description, name='edit_description'),

    path('projects', projects, name='projects'),
    path(
        'archived_projects', archived_projects,
        name='archived_projects'),

    path('rename_project', rename_project, name='rename_project'),
    path('archive_project', archive_project, name='archive_project'),
    path('unarchive_project', unarchive_project, name='unarchive_project'),

    path('settings', settings, name='settings_tracktime'),
    path('api_docs', api_docs, name='api_docs')]
