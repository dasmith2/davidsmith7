from invoice.tests.models.test_invoice import set_invoice_stuff
from tracktime.models.project_invoice import ProjectInvoice
from tracktime.tests.models.test_project import get_test_project


def get_test_project_invoice(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project()
  return set_invoice_stuff(ProjectInvoice(project=project), **kwargs)
