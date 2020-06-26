from django.db import models
from django.dispatch import receiver
from djaveClassMagic.signals import destroy_user

from tracktime.models.work_session import WorkSessionManager, WorkSession
from tracktime.models.project import Project


@receiver(destroy_user, sender=Project)
def destroy_user_project_work_sessions(sender, destroy_object=None, **kwargs):
  for project_work_session in destroy_object.projectworksession_set.all():
    destroy_user.send(
        sender=ProjectWorkSession, destroy_object=project_work_session)
    project_work_session.destroy()


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

  @classmethod
  def model_description(cls):
    return (
        'A ProjectWorkSession describes a single time span that a user worked '
        'on a Project.')

  def __repr__(self, nnow=None):
    return '<ProjectWorkSession {}: {} {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.date, self.project.name,
        self.status(nnow=nnow), self.hours)
