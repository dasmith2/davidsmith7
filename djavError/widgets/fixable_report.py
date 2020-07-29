
from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveClassMagic.edit_list_table import EditListTable
from djaveDT import now
from djaveForm.button import Button
from djaveForm.field import SelectField, Option
from djaveReport.date_range_report import DateRangeReport
from djavError.models.fixable import (
    get_fixables, default_status, default_from_date, EITHER, FIXED, NOT_FIXED)
from djaveTable.table import ButtonsCell


def get_fixable_status_filter():
  either = Option(EITHER, '')
  fixed = Option(FIXED, 'Fixed')
  not_fixed = Option(NOT_FIXED, 'Not fixed')
  return SelectField(
      'status', options=[either, fixed, not_fixed], default=default_status())


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
    self.setup_set_dt_green('fixed', 'Fixed', 'Not fixed')

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
