from datetime import date

from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.tests.models.test_work_session import get_test_work_session
from tracktime.tests.models.test_to_do import get_test_to_do
from tracktime.widgets.work_report import WorkReportContent


class WorkReportTests(TestCase):
  def test_display(self):
    user = get_test_user()
    get_test_work_session(
        user=user,
        date=date(2020, 1, 1),
        hours=1,
        started=to_tz_dt('2020-01-01 12:00'),
        stopped=to_tz_dt('2020-01-01 13:00'))
    get_test_to_do(
        creator=user, done=to_tz_dt('2020-01-01 12:30'),
        description='Shave bears')

    work_report = WorkReportContent(user, date(2020, 1, 1), date(2020, 1, 1))
    html = work_report.as_html()
    self.assertTrue(html.find('Shave bears') > 0)
