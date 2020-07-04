
from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveDT import now
from djaveForm.field import SelectField, Option
from djaveReport.date_range_report import DateRangeReport
from djavError.models.error import Error
from djavError.widgets.staff_email_log_report import (
    get_staff_email_logs, default_from_date, StaffEmailLogTable)
from djaveTable.cell_content import InHref


EITHER = 'either'
FIXED = 'fixed'
NOT_FIXED = 'not_fixed'


def default_status():
  return NOT_FIXED


def get_errors(
    from_date='use_default', to_date='use_default', status='use_default',
    nnow=None):
  errors = get_staff_email_logs(
      Error, from_date=from_date, to_date=to_date, nnow=nnow)
  if status == 'use_default':
    status = default_status()
  if status and status != EITHER:
    errors = errors.filter(fixed__isnull=status != FIXED)
  return errors


class ErrorsReport(DateRangeReport):
  def __init__(self, request_get, nnow=None):
    nnow = nnow or now()
    default_to_date = nnow.date()
    status = get_status_filter()
    filters = [status]
    super().__init__(
        default_from_date(nnow=nnow), default_to_date, request_get=request_get,
        filters=filters)
    self.set_contents(ErrorsTable(
        self.from_date(), self.to_date(), status.get_value_or_default()))


def get_status_filter():
  either = Option(EITHER, '')
  fixed = Option(FIXED, 'Fixed')
  not_fixed = Option(NOT_FIXED, 'Not fixed')
  return SelectField(
      'status', options=[either, fixed, not_fixed], default=default_status())


class ErrorsTable(StaffEmailLogTable):
  def __init__(self, from_date, to_date, status):
    self.from_date = from_date
    self.to_date = to_date
    self.status = status
    super().__init__(Error)
    self.js = render_to_string('errors.js', context={
        'ajax_update_url': reverse('ajax_update')})
    self.css = '.fixed { background-color: #dfd; }'

  def headers(self):
    return super().headers() + ['Fixed', '']

  def create_rows(self):
    for error in get_errors(self.from_date, self.to_date, self.status):
      view = InHref(
          'View', reverse('see_error', kwargs={'pk': error.pk}),
          classes=['button'])
      buttons = [view]
      fixed = bool(error.fixed)
      self.create_row(
          self.staff_email_log_cells(error) + [fixed, buttons],
          pk=error.pk, additional_attrs={'data-fixed': fixed})
