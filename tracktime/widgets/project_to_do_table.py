from tracktime.fields import project_field
from tracktime.models.latest_project import set_latest_project
from tracktime.models.project import Project
from tracktime.models.project_to_do import ProjectToDo
from tracktime.widgets.to_do_table import ToDoForm, ToDoTable


class ProjectToDoForm(ToDoForm):
  def __init__(self, user, do_all_projects):
    self.do_all_projects = do_all_projects
    self.user = user
    super().__init__()

  def create_fields(self):
    fields = super().create_fields()
    if self.do_all_projects:
      self.project_field = project_field(self.user)
      fields.append(self.project_field)
    return fields


class ProjectToDoTable(ToDoTable):
  def __init__(self, user, project, form_data, nnow=None):
    """ If project is None, show a project column and pull to do items from all
    projects. """
    self.project = project
    super().__init__(user, form_data, nnow=nnow)

  def do_all_projects(self):
    return not bool(self.project)

  def get_form(self):
    return ProjectToDoForm(self.user, do_all_projects=self.do_all_projects())

  def create_to_do(self):
    project = self.project
    if not project:
      project = Project.live.get(
          pk=self.form.project_field.get_value())
      set_latest_project(self.user, project)
    return ProjectToDo.live.create(
        creator=self.user, project=project,
        description=self.form.get_description())

  def cells_for_enter_new(self):
    cells = []
    if self.do_all_projects():
      cells.append(self.form.project_field)
    cells.extend(super().cells_for_enter_new())
    return cells

  def get_not_long_done(self):
    return ProjectToDo.live.not_long_done(self.user, self.project)

  def cells_for_existing(self, to_do):
    cells = []
    if self.do_all_projects():
      cells.append(to_do.project.name)
    cells.extend(super().cells_for_existing(to_do))
    return cells
