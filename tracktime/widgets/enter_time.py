from datetime import date

from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveCRUDTable.columns import ButtonsColumn
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.filters import hidden_filter, HIDDEN_NOT_DELETED_FILTER
from djaveHTML.button import Button

from tracktime.columns import ProjectColumn, HoursColumn
from tracktime.models.project_work_session import ProjectWorkSession


class EnterTimeButtonsColumn(ButtonsColumn):
  def __init__(self):
    super().__init__([Button('Delete')])


class EnterTime(CRUDTable):
  def __init__(self, user, day):
    self.user = user
    self.day = day
    display_columns = [
        ProjectColumn(user, has_to_do_list=None, use_clock=True),
        HoursColumn(), EnterTimeButtonsColumn()]
    hidden_filters = [
        hidden_filter('date', date.today().isoformat()),
        hidden_filter('hours', False, 'hours__isnull'),
        HIDDEN_NOT_DELETED_FILTER]
    save_new_defaults = {'user': 'me', 'date': 'today'}
    super().__init__(
        ProjectWorkSession, display_columns,
        save_new_defaults=save_new_defaults, list_url=reverse('enter_time'),
        confirm_delete_question='Delete?', hidden_filters=hidden_filters,
        inline_create=True, list_header=None, margin_top_css='margin-top-half',
        fetch_list_callback='put_sum_hours_in_header')
    self.add_js(render_to_string('js/enter_time.js'))
