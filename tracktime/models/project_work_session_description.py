from tracktime.models.work_session_description import WorkSessionDescriptions
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.models.project_to_do import ProjectToDo


class ProjectWorkSessionDescriptions(WorkSessionDescriptions):
  def __init__(
      self, project, user, from_date, to_date, tz_str, include_invoiced=True):
    self.project = project
    self.include_invoiced = include_invoiced
    super().__init__(user, from_date, to_date, tz_str)

  def list_params(self):
    return super().list_params() + [self.project]

  def show_project(self):
     return not self.project

  def get_work_session_descriptions(self):
    if self.include_invoiced:
      return self._work_session_descriptions
    to_return = []
    for wsd in self._work_session_descriptions:
      if wsd.work_session.projectlineitem_or_none is None or (
          wsd.work_session.projectlineitem.deleted):
        to_return.append(wsd)
    return to_return

  def get_work_sessions(self):
    work_sessions = super().get_work_sessions().select_related(
        'projectlineitem')
    if self.project:
      work_sessions = work_sessions.filter(project=self.project)
    return work_sessions

  def get_to_dos(self, work_sessions):
    to_dos = super().get_to_dos(work_sessions)
    if self.project:
      to_dos = to_dos.filter(project=self.project)
    return to_dos

  def time_description(self, work_session):
    description = super().time_description(work_session)
    if self.show_project():
      description = '{} {}'.format(work_session.project.name, description)
    return description

  def to_do_description(self, to_do):
    description = super().to_do_description(to_do)
    if self.show_project():
      description = '{} {}'.format(to_do.project.name, description)
    return description

  def work_session_class(self):
    return ProjectWorkSession

  def to_do_class(self):
    return ProjectToDo
