from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from tracktime.models.work_session import WorkSessionManager, WorkSession

from tracktime.models.project import Project


class ProjectWorkSessionManager(WorkSessionManager):
  pass


class ProjectWorkSession(WorkSession):
  # Rename this to project when I finish getting rid of the project field in
  # the base class.
  project_new = models.ForeignKey(
      Project, on_delete=models.PROTECT, null=True, blank=True)

  live = ProjectWorkSessionManager()


# Temporary so we can get that project field out of WorkSession
@receiver(post_save, sender=WorkSession)
def post_save_work_session(sender, instance, *args, **kwargs):
  existing = ProjectWorkSession.all.filter(worksession_ptr=instance).first()
  if existing:
    existing.project_new = instance.project
    existing.save()
  else:
    # Thanks
    # https://stackoverflow.com/questions/40084205/create-a-new-derived-object-from-an-existing-base-object-not-derived
    new_project_session = ProjectWorkSession(
        worksession_ptr=instance, project_new=instance.project)
    new_project_session.__dict__.update(instance.__dict__)
    new_project_session.save()
