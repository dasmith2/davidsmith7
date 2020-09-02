from djaveCRUDTable.crud_table import hidden_filter

from tracktime.models.project_to_do import ProjectToDo
from tracktime.widgets.to_dos import ToDos, ToDoButtonsColumn


class ProjectToDoButtonsColumn(ToDoButtonsColumn):
  def __init__(self, project):
    self.project = project
    super().__init__()

  def add_button_attrs(self, button):
    button.additional_attrs['data-project'] = self.project.pk


class ProjectToDos(ToDos):
  def __init__(self, project):
    self.project = project
    super().__init__(ProjectToDoButtonsColumn(project))

  def hidden_filters(self):
    filters = super().hidden_filters()
    filters.append(hidden_filter('project', self.project.pk))
    return filters

  def model(self):
    return ProjectToDo
