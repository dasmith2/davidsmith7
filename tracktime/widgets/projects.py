from django.shortcuts import reverse
from djaveCRUDTable.columns import (
    DisplayFieldColumn, EditDeleteColumn, ButtonsColumn)
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.filters import (
    HIDDEN_NOT_DELETED_FILTER, HIDDEN_DELETED_FILTER)
from djaveHTML.button import Button

from tracktime.models.project import Project


class Projects(CRUDTable):
  def __init__(self):
    filters = None
    list_url = reverse('projects')
    edit_delete_column = EditDeleteColumn(
        Project, delete_button_text='Archive', list_url=list_url)
    display_columns = [
        DisplayFieldColumn('Name', 'name'),
        edit_delete_column]
    edit_field_names_or_rows = [
        'name', 'use_clock', 'has_to_do_list', 'has_invoices']
    super().__init__(
        Project, display_columns, visible_filters=filters,
        edit_field_names_or_rows=edit_field_names_or_rows,
        save_new_defaults={'creator': 'me'},
        label_edit_page_with_field='name', list_url=list_url, list_header=None,
        confirm_delete_question=None,
        hidden_filters=[HIDDEN_NOT_DELETED_FILTER],
        saved_model_callback='post_save_project',
        deleted_model_callback='post_delete_project')
    self.add_js_from_template('js/projects.js')


class ArchivedProjects(CRUDTable):
  def __init__(self):
    filters = None
    display_columns = [
        DisplayFieldColumn('Name', 'name'),
        ButtonsColumn([Button('Un-archive')])]
    edit_field_names_or_rows = []
    list_url = reverse('archived_projects')
    super().__init__(
        Project, display_columns, visible_filters=filters,
        edit_field_names_or_rows=edit_field_names_or_rows, list_url=list_url,
        list_header='Archived', hidden_filters=[HIDDEN_DELETED_FILTER],
        can_create_new=False, modified_row_callback='setup_unarchive',
        nav_css_class='projects_nav')
