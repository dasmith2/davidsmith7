from datetime import date, timedelta

from django.shortcuts import reverse
from djaveCRUDTable.columns import DisplayFieldColumn
from djaveCRUDTable.filters import hidden_filter, from_filter, to_filter

from tracktime.columns import ProjectColumn
from tracktime.fields import project_field
from tracktime.models.project_to_do import ProjectToDo
from tracktime.models.to_do import get_status_filter, NOT_DONE
from tracktime.widgets.to_dos import ToDos, ToDoButtonsColumn


class ProjectToDoButtonsColumn(ToDoButtonsColumn):
  def __init__(self, project):
    self.project = project
    super().__init__()

  def add_button_attrs(self, button):
    button.additional_attrs['data-project'] = self.project.pk


class ProjectToDos(ToDos):
  def __init__(self, project, list_url):
    self.project = project
    self._list_url = list_url
    super().__init__()

  def columns(self):
    return super().columns() + [ProjectToDoButtonsColumn(self.project)]

  def hidden_filters(self):
    filters = super().hidden_filters()
    filters.append(hidden_filter('project', self.project.pk))
    return filters

  def model(self):
    return ProjectToDo

  def list_url(self):
    return self._list_url

  def get_list_api_url(self):
    return reverse('project_to_dos_for_ui')


class CreatedColumn(DisplayFieldColumn):
  def __init__(self):
    super().__init__('Created', 'create_date_str')

  def inline_create_cell(self):
    return '<th class="white-background">Created</th>'


class AllProjectToDos(ToDos):
  def __init__(self, user):
    self.user = user
    super().__init__()
    self.add_js_from_template('js/all_project_to_dos.js')

  def filters(self):
    default_from_date = date.today() - timedelta(days=365 / 2)
    project = project_field(
        self.user, label='Project', required=False, has_to_do_list=True)
    status = get_status_filter(default=NOT_DONE)
    return [
        from_filter('created', default_from_date),
        to_filter('created', date.today()), project, status]

  def columns(self):
    return [ProjectColumn(self.user)] + super().columns() + [
        ToDoButtonsColumn(), CreatedColumn()]

  def model(self):
    return ProjectToDo

  def list_url(self):
    return reverse('all_to_dos')
