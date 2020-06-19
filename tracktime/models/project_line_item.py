from django.db import models
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField

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
      ProjectWorkSession, on_delete=models.PROTECT, help_text=(
          'Which ProjectWorkSession does this ProjectLineItem represent? '
          'There may be only 1 ProjectLineItem per ProjectWorkSession, '
          'meaning that a single ProjectWorkSession may appear in 1 Invoice '
          'at most.'))

  @classmethod
  def model_description(cls):
    return (
        'A ProjectLineItem links a ProjectWorkSession to a ProjectInvoice. '
        'describe_service starts as the descriptions of the ProjectToDos that '
        'were marked "Done" during or immediately after the '
        'ProjectWorkSession.')

  live = LiveProjectLineItemManager()
