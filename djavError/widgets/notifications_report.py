from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from djavError.models.notification import Notification
from djavError.widgets.staff_email_log_report import (
    get_staff_email_logs, default_from_date, StaffEmailLogTable)


def get_notifications(
    from_date='use_default', to_date='use_default', nnow=None):
  return get_staff_email_logs(
      Notification, from_date=from_date, to_date=to_date, nnow=nnow)


class NotificationsReport(DateRangeReport):
  def __init__(self, request_get, nnow=None):
    nnow = nnow or now()
    default_to_date = nnow.date()
    super().__init__(
        default_from_date(nnow=nnow), default_to_date, request_get=request_get)
    self.set_contents(NotificationsTable(self.from_date(), self.to_date()))


class NotificationsTable(StaffEmailLogTable):
  def __init__(self, from_date, to_date):
    self.from_date = from_date
    self.to_date = to_date
    super().__init__(Notification)

  def headers(self):
    return super().headers() + ['Fixed', '']

  def create_rows(self):
    for notification in get_notifications(self.from_date, self.to_date):
      self.create_row(
          self.staff_email_log_cells(notification), pk=notification.pk)
