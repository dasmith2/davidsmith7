from django.urls import path

from tracktime.views.api_docs import api_docs
from tracktime.views.enter_time import enter_time, delete_work_session
from tracktime.views.invoices import (
    project_invoices, all_project_invoices, project_line_items,
    edit_project_invoice, view_project_invoice, project_invoice_rule)
from tracktime.views.projects import (
    projects, archived_projects, archive_project, unarchive_project)
from tracktime.views.report import (
    project_work_summary, project_work_report)
from tracktime.views.settings import settings
from tracktime.views.to_do import to_do, all_tasks


tracktime_urls = [
    path('', enter_time, name='enter_time'),
    path('to_do', to_do, name='to_do'),
    path('all_tasks', all_tasks, name='all_tasks'),
    path(
        'report', project_work_summary,
        name='project_work_summary'),
    path(
        'project_work_report', project_work_report,
        name='project_work_report'),

    path('invoices', project_invoices, name='project_invoices'),
    path('all_invoices', all_project_invoices, name='all_project_invoices'),
    path(
        'project_line_items', project_line_items,
        name='project_line_items'),
    path(
        'invoice/edit/<pk>', edit_project_invoice,
        name='edit_project_invoice'),
    path(
        'invoice/view/<pk>', view_project_invoice,
        name='view_project_invoice'),
    path('invoice_rule', project_invoice_rule, name='project_invoice_rule'),
    path(
        'invoice_rule/<pk>', project_invoice_rule,
        name='project_invoice_rule'),

    path(
        'delete_work_session', delete_work_session,
        name='delete_work_session'),

    path('projects', projects, name='projects'),
    path(
        'archived_projects', archived_projects,
        name='archived_projects'),

    path('archive_project', archive_project, name='archive_project'),
    path('unarchive_project', unarchive_project, name='unarchive_project'),

    path('settings', settings, name='settings_tracktime'),
    path('api_docs', api_docs, name='tracktime_api_docs')]
