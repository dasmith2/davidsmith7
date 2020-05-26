from djaveDT import str_to_tz_dt
from djaveTest import get_test_user

from tracktime.models.project import Project


def get_test_project(**kwargs):
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user()
  project = Project.live.create(
      name=kwargs.get('name', 'Time Tracker'), creator=creator)
  if 'created' in kwargs:
    created = str_to_tz_dt(kwargs['created'])
    Project.live.filter(pk=project.pk).update(created=created)
    project.refresh_from_db()
  return project
