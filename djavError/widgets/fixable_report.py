from datetime import timedelta

from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveClassMagic.edit_list_table import EditListTable
from djaveDT import now, end_of_day, beginning_of_day
from djaveForm.button import Button
from djaveForm.field import SelectField, Option
from djaveReport.date_range_report import DateRangeReport
from djaveTable.table import ButtonsCell


EITHER = 'either'
FIXED = 'fixed'
NOT_FIXED = 'not_fixed'
USE_DEFAULT = 'use_default'


def default_status():
  return NOT_FIXED


def default_from_date(nnow=None):
  nnow = nnow or now()
  return nnow.date() - timedelta(days=7)


def get_fixables(
    model, from_date=USE_DEFAULT, to_date=USE_DEFAULT, status=USE_DEFAULT,
    nnow=None):
  """ Assumes you have a created column and a fixed column. Easiest thing is to
  inherit from djavError.models.fixable I'm leaving this here instead of in
  djavError.models.fixable because this function knows about UI specific
  filters and defaults. """
  nnow = nnow or now()
  if from_date == USE_DEFAULT:
    from_date = default_from_date(nnow=nnow)
  if to_date == USE_DEFAULT:
    to_date = nnow.date()
  query_set = model.objects.filter(
      created__gte=beginning_of_day(from_date),
      created__lte=end_of_day(to_date)).order_by('-created')
  return do_fixed_filter(query_set, status)


def get_fixable_status_filter():
  either = Option(EITHER, '')
  fixed = Option(FIXED, 'Fixed')
  not_fixed = Option(NOT_FIXED, 'Not fixed')
  return SelectField(
      'status', options=[either, fixed, not_fixed], default=default_status())


def do_fixed_filter(query_set, status):
  if status == USE_DEFAULT:
    status = default_status()
  if status and status != EITHER:
    query_set = query_set.filter(fixed__isnull=status != FIXED)
  return query_set


class FixableTable(EditListTable):
  def __init__(self, from_date, to_date, status, nnow=None):
    super().__init__(self.get_model(), self.headers())
    pks = []
    for fixable in get_fixables(
        self.get_model(), from_date=from_date, to_date=to_date,
        status=status, nnow=nnow):
      pks.append(str(fixable.pk))
      cells = self.get_cells(fixable) + [
          ButtonsCell(self.get_buttons(fixable))]
      self.create_row(
          cells, pk=fixable.pk,
          additional_attrs={'data-fixed': bool(fixable.fixed)})

    last_header = ''
    if pks:
      last_header = Button('All fixed')
      all_fixed_url = reverse('all_fixed', kwargs={
          'model_name': self.get_model().__name__,
          'pks': ','.join(pks)})
      self.append_js(render_to_string(
          'all_fixed.js', context={'all_fixed_url': all_fixed_url}))
    self.headers.append(last_header)
    self.wire_up_set_dt_green('fixed', 'Fixed', 'Not fixed')

  def get_model(self):
    raise NotImplementedError('get_model')

  def headers(self):
    raise NotImplementedError('headers')

  def get_cells(self):
    raise NotImplementedError('get_cells')

  def get_buttons(self, fixable):
    return None


class FixableReport(DateRangeReport):
  def __init__(self, request_get, nnow=None):
    nnow = nnow or now()
    default_to_date = nnow.date()
    self.status_filter = get_fixable_status_filter()
    filters = [self.status_filter]
    super().__init__(
        default_from_date(nnow=nnow), default_to_date, request_get=request_get,
        filters=filters)
    self.set_contents(self.get_table())
