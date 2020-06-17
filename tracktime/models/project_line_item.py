from django.db import models
from djaveClass.one_to_one_or_none_field import OneToOneOrNoneField

from invoice.models.line_item import LineItem, LiveLineItemManager
from tracktime.models.project_work_session import ProjectWorkSession


def project_line_items(invoice):
  return ProjectLineItem.live.filter(invoice=invoice)


class LiveProjectLineItemManager(LiveLineItemManager):
  def get_line_items_from_invoices(self, invoices):
    return super().get_line_items_from_invoices(
        invoices).select_related('invoice__projectinvoice__project')


class ProjectLineItem(LineItem):
  project_work_session = OneToOneOrNoneField(
      ProjectWorkSession, on_delete=models.PROTECT)

  live = LiveProjectLineItemManager()
