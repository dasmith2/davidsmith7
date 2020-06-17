from djaveForm.field import DateField
from djaveReport.filtered_report import FilteredReport


FROM_DATE = 'from_date'
TO_DATE = 'to_date'


class DateRangeReport(FilteredReport):
  def __init__(
      self, default_from_date, default_to_date, request_get=None, filters=None,
      contents=None, from_filter_label='From'):
    self.from_date_field = DateField(
        key_prefix=FROM_DATE, default=default_from_date,
        label=from_filter_label)
    self.to_date_field = DateField(
        key_prefix=TO_DATE, default=default_to_date, label='To')
    date_filters = [self.from_date_field, self.to_date_field]
    dynamic_filters = self._validate_filters(filters)
    use_filters = date_filters + dynamic_filters
    super().__init__(request_get, use_filters, contents)
    if self.from_date_field.value_was_set() and (
        self.to_date_field.value_was_set()) and (
            self.from_date_field.get_value() > self.to_date_field.get_value()):
      self.from_date_field.set_invalid_reason(
          'It looks like "From" and "To" are in the wrong order')

  def from_date(self):
    return self.from_date_field.get_value_or_default()

  def to_date(self):
    return self.to_date_field.get_value_or_default()
