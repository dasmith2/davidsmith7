from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.to_do_project_picker import ToDoProjectPicker
from tracktime.tests.models.test_project import get_test_project


class ToDoProjectPickerTests(TestCase):
  def test_display(self):
    creator = get_test_user()
    project = get_test_project(creator=creator, name='Comb bears')
    html = ToDoProjectPicker(creator, {}).as_html()
    self.assertTrue(html.find('Comb bears') > 0)

    self.assertEqual(
        0, ProjectWorkSession.live.get_clock_never_stopped(creator).count())
    ToDoProjectPicker(creator, {'punchin_{}'.format(project.pk): 'yep'})
    self.assertEqual(
        1, ProjectWorkSession.live.get_clock_never_stopped(creator).count())
