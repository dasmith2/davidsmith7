from djavError.models.notification import Notification
from djavError.widgets.fixable_report import FixableReport
from djavError.widgets.staff_email_log_table import (
    StaffEmailLogTable)


class NotificationsReport(FixableReport):
  def get_table(self):
    return NotificationsTable(
        self.from_date(), self.to_date(),
        self.status_filter.get_value_or_default())


class NotificationsTable(StaffEmailLogTable):
  def get_model(self):
    return Notification
