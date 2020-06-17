from django.db import models

from invoice.models.invoice import Invoice, LiveInvoiceManager
from tracktime.models.project import Project


class LiveProjectInvoiceManager(LiveInvoiceManager):
  def get_invoices(
      self, user, created_from, created_to, project, status, nnow=None):
    qs = super().get_invoices(
        user, created_from, created_to, status, nnow=nnow)
    if project:
      project_id = project
      if isinstance(project, Project):
        project_id = project.pk
      qs = qs.filter(project_id=project_id)
    return qs


class ProjectInvoice(Invoice):
  project = models.ForeignKey(Project, on_delete=models.PROTECT)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return super().filter_allowed_by_user(
        user, query_set).select_related('project')

  live = LiveProjectInvoiceManager()
