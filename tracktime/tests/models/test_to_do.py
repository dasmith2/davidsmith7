from djaveTest import TestCase, get_test_user
from djaveDT import str_to_tz_dt

from tracktime.models.to_do import ToDo
from tracktime.tests.models.test_project import get_test_project


def get_test_to_do(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  to_do = ToDo.objects.create(
      description=kwargs.get('description', 'Do some stuff'),
      done=kwargs.get('done', None),
      project=project,
      user=user)
  if 'created' in kwargs:
    ToDo.objects.filter(pk=to_do.pk).update(
        created=str_to_tz_dt(kwargs['created']))
    to_do.refresh_from_db()
  return to_do


class ToDoTests(TestCase):
  def test_not_done(self):
    project_1 = get_test_project(name='Time Tracker')
    project_2 = get_test_project(name='Davespace')
    user = get_test_user()

    not_done_1 = get_test_to_do(project=project_1, user=user)
    not_done_2 = get_test_to_do(project=project_2, user=user)
    # Done. Should never show up.
    get_test_to_do(
        project=project_1, done=str_to_tz_dt('2020-01-01'), user=user)

    self.assertEqual(
        [not_done_2, not_done_1], list(ToDo.objects.not_done(user)))
    self.assertEqual(
        [not_done_1], list(ToDo.objects.not_done(user, project_1)))

  def test_as_json(self):
    project = get_test_project()
    user = get_test_user()
    to_do = get_test_to_do(
        description='Hello world', done=None, project=project, user=user,
        created='2020-01-01 13:00')
    expected = dict(
        pk=to_do.pk,
        description='Hello world',
        created='2020-01-01T13:00:00-05:00',
        done=None,
        project=project.pk,
        user=user.pk)
    self.assertEqual(expected, to_do.as_json())

    to_do.done = str_to_tz_dt('2020-01-02 11:00')
    expected['done'] = '2020-01-02T11:00:00-05:00'
    self.assertEqual(expected, to_do.as_json())
