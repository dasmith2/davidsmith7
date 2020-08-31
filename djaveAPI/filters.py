from collections import namedtuple
from datetime import date

from django.utils.dateparse import parse_datetime, parse_date
from djaveAPI.paged_results import PAGE
from djaveClassMagic.model_fields import (
    model_fields, DATE_TIME, DATE, FLOAT, INTEGER, BOOLEAN)
from djaveAPI.problem import Problem
from djaveDT import to_tz_dt


def filter_model(model, credentials, request_GET):
  queryset = credentials.allowed_list(model)
  for _filter in get_filters(model, request_GET):
    field = _filter.filter_field
    if field.foreign_key_to:
      queryset = _filter_foreign_key(
          queryset, field, _filter.operator, _filter.value)
    else:
      key = field.name
      if _filter.operator:
        key = '{}__{}'.format(key, _filter.operator)
      queryset = queryset.filter(**{key: _filter.value})
  return queryset


ISNULL = 'isnull'
AVAILABLE_OPERATORS = ['gt', 'gte', 'lt', 'lte', ISNULL]


Filter = namedtuple('Filter', 'filter_field operator value')


def get_filters(model, request_GET):
  _available_filter_fields = available_filter_fields(model)
  filters = []
  for key, value in request_GET.items():
    if key == PAGE or not value:
      continue
    field_name, operator = field_operator(key)
    if field_name not in _available_filter_fields:
      raise Problem((
          '{} is not an available filter on {}. The available filters are '
          '{}').format(
              field_name, model.__name__,
              ', '.join(_available_filter_fields.keys())))
    if operator and operator not in AVAILABLE_OPERATORS:
      raise Problem((
          'You tried to filter on {}, but {} is not an available operator. '
          'The available operators are {}').format(
              key, operator, ', '.join(AVAILABLE_OPERATORS)))
    filter_field = _available_filter_fields[field_name]
    if operator == ISNULL:
      value = value.lower() == 'true'
    else:
      value = _parsed_value(filter_field, value)
    filters.append(Filter(filter_field, operator, value))
  return filters


def available_filter_fields(model):
  to_return = {}
  for field in model_fields(model):
    if field.can_filter:
      to_return[field.name] = field
  return to_return


def _parsed_value(field, value):

  def _raise_problem():
    if field.type == DATE_TIME:
      example = to_tz_dt('2020-01-15 12:00').isoformat()
    elif field.type == DATE:
      example = date(2020, 1, 15).isoformat()
    elif field.type == FLOAT:
      example = '12.34'
    elif field.type == INTEGER:
      example = '123'
    elif field.type == BOOLEAN:
      example = 'true'
    else:
      raise Exception(
          'I dont know how to explain an example {}'.format(field.type))
    raise Problem((
        'Your {} filter is set to {}, which I was unable to parse. '
        'An example of something I can parse is '
        '{}').format(field.name, value, example))

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
    elif field.type == BOOLEAN:
      to_return = value.lower() == 'true'
    else:
      raise Exception(
          'I dont know how to filter on type {}'.format(field.type))
  except ValueError:
    _raise_problem()
  # As per Django's annoying habit, parse_date and parse_datetime swallow
  # errors and simply return None.
  if to_return is None:
    _raise_problem()
  return to_return


def _filter_foreign_key(queryset, field, operator, value):
  if operator and operator != ISNULL:
    raise Problem((
        'When it comes to foreign key filters, I only support '
        'equivalence or isnull, e.g., {field_name}=12345 or '
        '{field_name}__isnull=true. A range '
        'filter like {field_name}__{operator} is invalid.').format(
            field_name=field.name, operator=operator))
  if field.type != INTEGER:
    raise Exception('I dont know how to handle non-integer IDs yet')
  key = field.name
  if operator:
    key = '{}__{}'.format(field.name, operator)
  return queryset.filter(**{key: value})


def field_operator(key):
  """ Given, like, submitted__gte, return ('submitted', 'gte') """
  if key.find('__') >= 0:
    return key.split('__')
  return (key, None)
