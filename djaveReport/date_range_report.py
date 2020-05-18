from djaveForm.field import DateField
from djaveReport.filtered_report import FilteredReport


class DateRangeReport(FilteredReport):
  def __init__(
      self, default_from_date, default_to_date, request_get=None, filters=None,
      contents=None):
    self.from_date_field = DateField(
        key_prefix='from_date', default=default_from_date, label='From')
    self.to_date_field = DateField(
        key_prefix='to_date', default=default_to_date, label='To')
    date_filters = [self.from_date_field, self.to_date_field]
    dynamic_filters = self._validate_filters(filters)
    use_filters = date_filters + dynamic_filters
    super().__init__(request_get, use_filters, contents)

  def from_date(self):
    return self.from_date_field.get_value_or_default()

  def to_date(self):
    return self.to_date_field.get_value_or_default()
