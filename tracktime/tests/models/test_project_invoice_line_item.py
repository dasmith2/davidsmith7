from invoice.tests.models.test_invoice_line_item import (
    set_invoice_line_item_stuff)
from tracktime.tests.models.test_project_work_session import (
    get_test_project_work_session)
from tracktime.models.project_invoice_line_item import ProjectInvoiceLineItem


def get_test_project_invoice_line_item(**kwargs):
  project_work_session = kwargs.get('project_work_session', None)
  if not project_work_session:
    project_work_session = get_test_project_work_session(**kwargs)
  instance = ProjectInvoiceLineItem(project_work_session=project_work_session)
  return set_invoice_line_item_stuff(instance, **kwargs)
