from collections import namedtuple
from datetime import date

from django.shortcuts import reverse
from django.template import loader
from djaveAPI.discover_schema import (
    api_fields, DATE_TIME, DATE, INTEGER, FLOAT)
from djaveAPI.widgets.field_table import field_table
from djaveDT import to_tz_dt
from djaveClass.find_models import model_from_name
from djaveURL import dict_as_query


def model_api_docs(model_name, api_root_url):
  model = model_from_name(model_name)
  template = loader.get_template('model_api_docs.html')
  model_description = None
  if hasattr(model, 'model_description'):
    model_description = model.model_description()
  else:
    model_description = 'Somebody go put def model_description() in {}'.format(
        model_name)
  # HAck! Fix this when I have a good example.
  model_plural_name = '{}s'.format(model_name)
  context = {
      'model_name': model_name,
      'model_plural_name': model_plural_name,
      'model_description': model_description,
      'fields_table': field_table(model),
      'examples': model_api_examples(model, api_root_url)}
  return template.render(context)


APIExample = namedtuple('APIExample', 'title code')


def model_api_examples(model, api_root_url):
  """
  -d, --data <data> Sends the specified data in a POST request
  -i, --include Include the HPPT response headers in the output
  -u, --user <user:password> Used for server authentication.
  -X, --request <command> use a custom request method. PUT, DELETE
  """
  basic_get = """curl -u <api_key_username>:<api_key_password> {}"""
  list_url = '{}{}'.format(api_root_url, reverse(
      'list_objects', kwargs={'model_name': model.__name__}))
  list_with_filters_url = '{}{}'.format(
      list_url, dict_as_query(example_filters(model)))
  get_one_url = '{}/{}'.format(list_url, 1234)
  examples = [APIExample('Get all', basic_get.format(list_url))]
  if list_url != list_with_filters_url:  # a.k.a. filters exist
    examples.append(APIExample('Get a filtered list', basic_get.format(
        list_with_filters_url)))
  examples.extend([
      APIExample('Get one', basic_get.format(get_one_url)),
      APIExample('Create', ''),
      APIExample('Update', ''),
      APIExample('"Delete"', '')])
  return examples


def example_filters(model):
  filters = {}
  for field in api_fields(model):
    if field.can_filter:
      name = field.name
      name__gte = '{}__gte'.format(name)
      name__lte = '{}__lte'.format(name)
      if field.foreign_key_to:
        filters[name] = 4321
      elif field.type == DATE_TIME:
        filters[name__gte] = to_tz_dt('2020-02-01 00:00').isoformat()
        filters[name__lte] = to_tz_dt('2020-02-28 23:59').isoformat()
      elif field.type == DATE:
        filters[name__gte] = date(2020, 2, 1).isoformat()
        filters[name__lte] = date(2020, 2, 28).isoformat()
      elif field.type == INTEGER:
        filters[name__gte] = 10
        filters[name__lte] = 20
      elif field.type == FLOAT:
        filters[name__gte] = 100.1
        filters[name__lte] = 200.2
      else:
        raise Exception(
            'I am not sure what an example {} filter looks like'.format(
                field.type))
  return filters
