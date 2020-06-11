from invoice.tests.models.test_line_item import (
    set_line_item_stuff)
from tracktime.tests.models.test_project_work_session import (
    get_test_project_work_session)
from tracktime.models.project_line_item import ProjectLineItem


def get_test_project_line_item(**kwargs):
  project_work_session = kwargs.get('project_work_session', None)
  if not project_work_session:
    project_work_session = get_test_project_work_session(**kwargs)
  instance = ProjectLineItem(project_work_session=project_work_session)
  return set_line_item_stuff(instance, **kwargs)
