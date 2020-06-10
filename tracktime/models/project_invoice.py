from django.db import models

from invoice.models.invoice import Invoice
from tracktime.models.project import Project


class ProjectInvoice(Invoice):
  project = models.ForeignKey(Project, on_delete=models.PROTECT)

  @classmethod
  def allowed_for_user_live(cls, user):
    return super().allowed_for_user_live(user).select_related('project')
