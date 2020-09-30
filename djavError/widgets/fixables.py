from djaveCRUDTable.columns import DisplayFieldColumn, ButtonsColumn
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.filters import from_filter, to_filter
from djaveHTML.button import Button
from djaveHTML.field import SelectField, Option


def get_fixable_status_filter():
  either = Option('', '')
  fixed = Option(False, 'Fixed')
  not_fixed = Option(True, 'Not fixed')
  return SelectField(
      'status', options=[either, fixed, not_fixed], default=not_fixed,
      query_key='fixed__isnull')


class FixedColumn(ButtonsColumn):
  def __init__(self, extra_buttons):
    not_fixed_button = Button('Not fixed', css_classes=['start-hidden'])
    super().__init__(extra_buttons + [Button('Fixed'), not_fixed_button])

  def buttons_header(self):
    return Button('All fixed')


class Fixables(CRUDTable):
  def __init__(self):
    visible_filters = [
        from_filter('latest', label='Latest from'), to_filter('latest'),
        get_fixable_status_filter()]
    super().__init__(
        self.get_model(), self.get_columns(), visible_filters=visible_filters,
        modified_row_callback='modified_fixable_row_callback',
        list_header=None, can_create_new=False, hidden_filters=[])
    self.add_js_from_template('js/fixed.js')

  def get_model(self):
    raise NotImplementedError('get_model')

  def get_leading_columns(self):
    raise NotImplementedError('get_leading_columns')

  def get_columns(self):
    middle_columns = [
        DisplayFieldColumn('Latest', 'latest_str'),
        DisplayFieldColumn('Fixed', 'fixed_str'),
        DisplayFieldColumn('Count')]
    return self.get_leading_columns() + middle_columns + (
        self.get_tail_columns() + [FixedColumn(self.get_extra_buttons())])

  def get_tail_columns(self):
    return []

  def get_extra_buttons(self):
    return []
