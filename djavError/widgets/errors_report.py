from django.shortcuts import reverse
from djavError.models.error import Error
from djavError.widgets.fixable_report import FixableReport
from djavError.widgets.staff_email_log_table import StaffEmailLogTable
from djaveTable.cell_content import InHref


class ErrorsReport(FixableReport):
  def get_table(self):
    return ErrorsTable(
        self.from_date(), self.to_date(),
        self.status_filter.get_value_or_default())


class ErrorsTable(StaffEmailLogTable):
  def get_model(self):
    return Error

  def get_buttons(self, staff_email_log):
    return InHref(
        'View', reverse('see_error', kwargs={'pk': staff_email_log.pk}),
        button=True)
