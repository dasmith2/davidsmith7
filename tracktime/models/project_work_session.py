from django.db import models
from tracktime.models.work_session import WorkSessionManager, WorkSession

from tracktime.models.project import Project


class ProjectWorkSessionManager(WorkSessionManager):
  def select_related_list(self):
    return super().select_related_list() + ['project']


class ProjectWorkSession(WorkSession):
  # Rename this to project when I finish getting rid of the project field in
  # the base class.
  project = models.ForeignKey(
      Project, on_delete=models.PROTECT, help_text=(
          'What project did the user work on in this work session?'))

  live = ProjectWorkSessionManager()

  def model_description():
    return (
        'A ProjectWorkSession describes a single time span that a user worked '
        'on a Project.')

  def as_json(self, nnow=None):
    base_dict = super().as_json(nnow=nnow)
    base_dict['project'] = self.project.pk
    return base_dict

  def __repr__(self, nnow=None):
    return '<ProjectWorkSession {}: {} {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.date, self.project.name,
        self.status(nnow=nnow), self.hours)
