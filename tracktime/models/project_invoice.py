from django.db import models

from invoice.models.invoice import Invoice
from tracktime.models.project import Project


class ProjectInvoice(Invoice):
  project = models.ForeignKey(Project, on_delete=models.PROTECT)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return super().filter_allowed_by_user(
        user, query_set).select_related('project')
