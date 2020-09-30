from datetime import date, timedelta
from djaveHTML.field import HiddenField, DateField


def hidden_filter(field_name, value, data_query_key=None):
  return HiddenField(
      field_name, value=value,
      **{'data-query-key': data_query_key or field_name})


HIDDEN_NOT_DELETED_FILTER = hidden_filter('deleted', 'true', 'deleted__isnull')
HIDDEN_DELETED_FILTER = hidden_filter('deleted', 'false', 'deleted__isnull')


def from_filter(query_key_prefix, default=None, label=None):
   default = default or date.today() - timedelta(days=7)
   field = DateField(
       'from_date', default=default, label=label or 'From',
       query_key='{}__gte'.format(query_key_prefix))
   field.do_beginning_of_day()
   return field


def to_filter(query_key_prefix, default=None):
  default = default or date.today()
  field = DateField(
      'to_date', default=default, label='To',
      query_key='{}__lte'.format(query_key_prefix))
  field.do_end_of_day()
  return field
