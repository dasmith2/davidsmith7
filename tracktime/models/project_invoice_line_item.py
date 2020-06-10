from django.db import models
from djaveClass.one_to_one_or_none_field import OneToOneOrNoneField

from invoice.models.invoice_line_item import InvoiceLineItem
from tracktime.models.project_work_session import ProjectWorkSession


def project_invoice_line_items(invoice):
  return ProjectInvoiceLineItem.live.filter(invoice=invoice)


class ProjectInvoiceLineItem(InvoiceLineItem):
  project_work_session = OneToOneOrNoneField(
      ProjectWorkSession, on_delete=models.PROTECT)
