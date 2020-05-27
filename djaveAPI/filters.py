from datetime import date

from django.utils.dateparse import parse_datetime, parse_date
from djaveAPI.discover_schema import (
    api_fields, DATE_TIME, DATE, FLOAT, INTEGER)
from djaveDT import to_tz_dt
from djAveJAX import AjaxProblem


AVAILABLE_OPERATORS = ['gt', 'gte', 'lt', 'lte']


def filter_model(model, api_key, request_GET):
  queryset = model.all.allowed(api_key)
  available_filters = filters(model)
  for key, value in request_GET.items():
    if not value:
      continue
    field_name, operator = field_operator(key)
    if field_name not in available_filters:
      raise AjaxProblem((
          '{} is not an available filter on {}. The available filters are '
          '{}').format(
          field_name, model.__name__, ', '.join(available_filters.keys())))
    if operator and operator not in AVAILABLE_OPERATORS:
      raise AjaxProblem((
          'You tried to filter on {}, but {} is not an available operator. '
          'The available operators are {}').format(
              key, operator, ', '.join(AVAILABLE_OPERATORS)))
    field = available_filters[field_name]
    if field.foreign_key_to:
      queryset = _filter_foreign_key(queryset, field, operator, value)
    else:
      queryset = queryset.filter(**{key: _parsed_value(field, key, value)})
  return queryset


def _parsed_value(field, key, value):

  def _raise_problem():
    if field.type == DATE_TIME:
      example = to_tz_dt('2020-01-15 12:00').isoformat()
    elif field.type == DATE:
      example = date(2020, 1, 15).isoformat()
    elif field.type == FLOAT:
      example = '12.34'
    elif field.type == INTEGER:
      example = '123'
    else:
      raise Exception(
          'I dont know how to explain an example {}'.format(field.type))
    raise AjaxProblem((
        'Your {} filter is set to {}, which I was unable to parse. '
        'An example of something I can parse is '
        '{}').format(key, value, example))

  # As per Django's annoying habit, parse_date and parse_datetime swallow
  # errors and simply return None.
  to_return = None
  try:
    if field.type == DATE_TIME:
      to_return = parse_datetime(value)
    elif field.type == DATE:
      to_return = parse_date(value)
    elif field.type == FLOAT:
      to_return = float(value)
    elif field.type == INTEGER:
      to_return = int(value)
    else:
      raise Exception(
          'I dont know how to filter on type {}'.format(field.type))
  except ValueError:
    _raise_problem()
  if to_return is None:
    _raise_problem()
  return to_return


def _filter_foreign_key(queryset, field, operator, value):
  if operator:
    raise AjaxProblem((
        'When it comes to foreign key filters, I only support a single '
        'id like {}=12345. A range filter like {}__{} is invalid.').format(
            field.name, field.name, operator))
  if field.type != INTEGER:
    raise Exception('I dont know how to handle non-integer IDs yet')
  try:
    value = int(value)
  except ValueError:
    raise AjaxProblem((
        'The {} filter should be an integer. You specified: '
        '{}').format(field.name, value))
  return queryset.filter(**{field.name: value})


def field_operator(key):
  """ Given, like, submitted__gte, return ('submitted', 'gte') """
  if key.find('__') >= 0:
    return key.split('__')
  return (key, None)


def filters(model):
  to_return = {}
  for field in api_fields(model):
    if field.can_filter:
      to_return[field.name] = field
  return to_return
