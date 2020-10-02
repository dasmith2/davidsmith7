from django.urls import path, re_path

from tracktime.views.api_docs import api_docs
from tracktime.views.enter_time import enter_time
from tracktime.views.invoices import (
    project_invoices, all_project_invoices, project_line_items,
    view_project_invoice,
    create_invoice, list_or_save_new_line_item,
    get_save_or_delete_existing_line_item)
from tracktime.views.nav_context import SETTINGS
from tracktime.views.projects import projects, archived_projects
from tracktime.views.report import (
    project_work_summary, project_work_report, project_work_summary_data,
    project_work_session_description_data)
from tracktime.views.settings import settings
from tracktime.views.to_do import (
    to_dos, all_to_dos, list_or_save_new_project_to_do,
    get_save_or_delete_existing_project_to_do)


tracktime_urls = [
    path('clock', enter_time, name='enter_time'),

    re_path(r'^to_dos/project/(?P<project_pk>\d+).*$', to_dos, name='to_dos'),
    re_path(r'^to_dos.*$', to_dos, name='to_dos'),
    re_path(r'^all_to_dos.*$', all_to_dos, name='all_to_dos'),

    path(
        'report', project_work_summary,
        name='project_work_summary'),
    path(
        'project_work_report', project_work_report,
        name='project_work_report'),
    path(
        'api/project_work_summary_data', project_work_summary_data,
        name='project_work_summary_data'),
    path(
        'api/project_work_session_description_data',
        project_work_session_description_data,
        name='project_work_session_description_data'),

    re_path(r'^invoices.*$', project_invoices, name='project_invoices'),
    re_path(
        r'^project_invoice_rules.*$', project_invoices,
        name='project_invoice_rules'),
    path('all_invoices', all_project_invoices, name='all_project_invoices'),
    path(
        'project_line_items', project_line_items,
        name='project_line_items'),
    path(
        'invoice/view/<pk>', view_project_invoice,
        name='view_project_invoice'),

    re_path(r'^project.*$', projects, name='projects'),
    path(
        'archived_projects', archived_projects,
        name='archived_projects'),

    path('settings', settings, name=SETTINGS),
    path('api_docs', api_docs, name='tracktime_api_docs'),

    path('api/create_invoice', create_invoice, name='create_invoice'),
    path(
        'api/line_items_for_ui', list_or_save_new_line_item,
        name='list_or_save_new_line_item'),
    path(
        'api/line_items_for_ui/<pk>', get_save_or_delete_existing_line_item,
        name='get_save_or_delete_existing_line_item'),

    path(
        'api/project_to_dos_for_ui', list_or_save_new_project_to_do,
        name='list_or_save_new_project_to_do'),
    path(
        'api/project_to_dos_for_ui/<pk>',
        get_save_or_delete_existing_project_to_do,
        name='get_save_or_delete_existing_project_to_do')]
