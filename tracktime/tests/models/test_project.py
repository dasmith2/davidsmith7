from djaveDT import str_to_tz_dt

from tracktime.models.project import Project


def get_test_project(**kwargs):
  project = Project.live.create(name=kwargs.get('name', 'Time Tracker'))
  if 'created' in kwargs:
    created = str_to_tz_dt(kwargs['created'])
    Project.live.filter(pk=project.pk).update(created=created)
    project.refresh_from_db()
  return project
