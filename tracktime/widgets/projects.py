from django.shortcuts import reverse
from djaveCRUDTable.crud_table import (
    CRUDTable, DisplayFieldColumn, EditDeleteColumn, ButtonsColumn,
    HIDDEN_NOT_DELETED_FILTER, HIDDEN_DELETED_FILTER)

from tracktime.models.project import Project


class Projects(CRUDTable):
  def __init__(self):
    filters = None
    display_columns = [
        DisplayFieldColumn('Name', 'name'),
        EditDeleteColumn(Project, delete_button_text='Archive')]
    edit_field_names = ['name', 'use_clock', 'has_to_do_list', 'has_invoices']
    list_url = reverse('projects')
    super().__init__(
        Project, filters, display_columns, edit_field_names,
        save_new_defaults={'creator': 'me'}, label_edit_page_with_field='name',
        list_url=list_url, list_header=None, delete_row_confirm_question=None,
        hidden_filters=[HIDDEN_NOT_DELETED_FILTER])


class ArchivedProjects(CRUDTable):
  def __init__(self):
    filters = None
    display_columns = [DisplayFieldColumn('Name', 'name')]
    edit_field_names = []
    list_url = reverse('archived_projects')
    super().__init__(
        Project, filters, display_columns, edit_field_names,
        list_url=list_url, list_header='Archived',
        hidden_filters=[HIDDEN_DELETED_FILTER], can_create_new=False)
