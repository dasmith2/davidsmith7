from datetime import timedelta

from djaveClassMagic.edit_list_table import EditListTable
from djaveDT import beginning_of_day, end_of_day, now


def default_from_date(nnow=None):
  nnow = nnow or now()
  return nnow.date() - timedelta(days=7)


def get_staff_email_logs(
    model, from_date='use_default', to_date='use_default', nnow=None):
  nnow = nnow or now()
  if from_date == 'use_default':
    from_date = default_from_date(nnow=nnow)
  if to_date == 'use_default':
    to_date = nnow.date()
  return model.objects.filter(
      created__gte=beginning_of_day(from_date),
      created__lte=end_of_day(to_date)).order_by('-created')


class StaffEmailLogTable(EditListTable):
  def __init__(self, model):
    super().__init__(model, self.headers())
    self.create_rows()

  def headers(self):
    return ['Title', 'Created', 'Latest', 'Count']

  def staff_email_log_cells(self, staff_email_log):
    return [
        staff_email_log.title, staff_email_log.created, staff_email_log.latest,
        staff_email_log.count]
