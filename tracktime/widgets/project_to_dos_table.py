from tracktime.fields import project_field
from tracktime.models.latest_project import set_latest_project
from tracktime.models.project import Project
from tracktime.models.project_to_do import ProjectToDo
from tracktime.widgets.to_dos_table import ToDoForm, ToDosTable


class ProjectToDoForm(ToDoForm):
  def __init__(self, user, do_all_projects):
    self.do_all_projects = do_all_projects
    self.user = user
    super().__init__()

  def create_fields(self):
    fields = super().create_fields()
    if self.do_all_projects:
      self.project_field = project_field(self.user, has_to_do_list=True)
      fields.append(self.project_field)
    return fields


class ProjectToDosTable(ToDosTable):
  def __init__(self, user, form_data, project=None, nnow=None):
    self.project = project
    super().__init__(user, form_data, nnow=nnow)

  def do_all_projects(self):
    return not bool(self.project)

  def get_form(self):
    return ProjectToDoForm(self.user, do_all_projects=self.do_all_projects())

  def get_headers(self):
    headers = []
    if self.should_filter_created():
      if not self.project:
        headers.append('Project')
      headers.extend(['Description', '', 'Created'])
    return headers

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

  def get_to_dos(self):
    to_dos = super().get_to_dos()

    manager = self.to_do_class().live
    if self.project:
      to_dos = manager.filter_project(to_dos, self.project)

    return to_dos

  def to_do_class(self):
    return ProjectToDo

  def cells_for_existing(self, to_do):
    cells = []
    if self.do_all_projects():
      cells.append(to_do.project.name)
    cells.extend(super().cells_for_existing(to_do))
    return cells
