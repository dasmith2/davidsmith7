from django.db import models
from django.dispatch import receiver
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField
from djaveClassMagic.signals import destroy_user

from invoice.models.line_item import LineItem, LiveLineItemManager
from tracktime.models.project_work_session import ProjectWorkSession


@receiver(destroy_user, sender=ProjectWorkSession)
def destroy_user_project_line_items(sender, destroy_object=None, **kwargs):
  project_line_item = destroy_object.projectlineitem_or_none
  if project_line_item:
    project_line_item.destroy()


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
          'There can be only one ProjectLineItem per ProjectWorkSession.'))

  @classmethod
  def model_description(cls):
    return (
        'A ProjectLineItem links a ProjectWorkSession to a ProjectInvoice. '
        'describe_service starts as the descriptions of the ProjectToDos that '
        'were marked "Done" during or immediately after the '
        'ProjectWorkSession.')

  live = LiveProjectLineItemManager()
