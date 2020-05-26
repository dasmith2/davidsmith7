from djaveTest import TestCase, get_test_user

from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_to_do import get_test_to_do
from tracktime.tests.models.test_project_work_session import (
    get_test_project_work_session)


class TestCaseWithData(TestCase):
  def setup_user(self):
    self.user = get_test_user()

  def setup_projects(self):
    self.project_1 = get_test_project(name='Project 1')
    self.project_2 = get_test_project(name='Project 2')

  def setup_work_sessions(self):
    self.work_session_1 = get_test_project_work_session(
        user=self.user, project=self.project_1, hours=1.1, date='2020-01-15',
        started='2020-01-15 11:00', stopped='2020-01-15 12:06')
    self.work_session_2 = get_test_project_work_session(
        user=self.user, project=self.project_1, hours=2.1, date='2020-01-15')

  def setup_to_dos(self):
    self.to_do = get_test_to_do(
        creator=self.user, project=self.project_1,
        description='Glue the arms on the manikin', done='2020-01-15 11:30',
        done_by=self.user)

  def setup_irrelevant_stuff(self):
    get_test_user(username='irrelevant_user')
    get_test_project_work_session(  # Wrong day
        user=self.user, project=self.project_1, hours=20.0, date='2020-01-05')
    get_test_project_work_session(  # Wrong user
        user=get_test_user(), project=self.project_1, hours=30.8,
        date='2020-01-15')
    get_test_project_work_session(  # Deleted
        user=self.user, project=self.project_1, hours=40.0, date='2020-01-15',
        started='2020-01-15 11:00', stopped='2020-01-15 12:06',
        deleted='2020-01-15 12:08')
    get_test_project_work_session(  # The clock is running
        user=self.user, project=self.project_1, date='2020-01-15',
        started='2020-01-15 10:00', stopped=None)

    get_test_to_do(  # Not done yet
        creator=self.user, project=self.project_1,
        description='Drink the leftover coffee')
    get_test_to_do(  # Done a long time ago
        creator=self.user, done_by=self.user, project=self.project_1,
        description='I\'m going to not vote yes', done='2020-01-05')
