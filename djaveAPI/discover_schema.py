""" Dig through all the models and calculate the API schema, which will inform
the documentation and the API itself. """
from collections import namedtuple
import re

from django.conf import settings
from django.db.models.fields.reverse_related import ManyToOneRel
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveClass.find_models import models_in_app


def use_publishable(instance, publishable_class=None):
  """ Returns a (model, instance) tuple. The entire point of this is wiring
  Django's user model into the API. """
  model = None
  if publishable_class:
    model = publishable_class
    if issubclass(model, PretendPublishable):
      instance = model(instance)
  elif isinstance(instance, Publishable):
    model = instance.__class__
  else:
    raise Exception(
        '{} is not a Publishable class, so I need you to tell me what '
        'PretendPublishable class I should use.'.format(
            instance.__class__.__name__))
  return model, instance


def publishable_models():
  to_return = []
  for app_name in settings.INSTALLED_APPS:
    to_return.extend(publishable_models_in_app(app_name))
  return to_return


def publishable_models_in_app(app_name):
  return models_in_app(app_name, Publishable) + models_in_app(
      app_name, PretendPublishable)


def publishable_model_from_name(model_name):
  for model in publishable_models():
    if model.__name__ == model_name:
      return model


APIField = namedtuple('APIField', [
    'name', 'help_text', 'can_filter', 'type', 'foreign_key_to', 'max_length',
    'required', 'editable'])

DATE_TIME = 'DateTime'
DATE = 'Date'
FLOAT = 'Float'
INTEGER = 'Integer'
TEXT = 'Text'
CHAR = 'Char'
BOOLEAN = 'Boolean'
TYPES = [DATE_TIME, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN]


def api_fields(model):
  fields = []
  for field in model.get_model_fields_for_api():
    name = field.name
    is_ptr_to_base_class = re.compile(r'\w+_ptr').findall(name)
    if is_ptr_to_base_class:
      continue
    if isinstance(field, ManyToOneRel):
      continue

    can_filter = field.db_index
    help_text = field.help_text
    field_type = field.get_internal_type()
    required = not field.null
    editable = field.editable
    foreign_key_to = None
    max_length = None

    is_id = name == 'id'
    if is_id:
      required = False
      can_filter = False
      editable = False
      help_text = 'What is the primary key for this object?'
      field_type = 'Integer'
    else:
      field_type = field_type.replace('Field', '')
      if field_type == 'ForeignKey':
        try:
          field.get_prep_value(1)
        except ValueError:
          raise Exception(
              'The API doesnt know how to handle non-integer primary keys '
              'yet. See filter_model in djaveAPI.filters specifically')
        field_type = INTEGER
        foreign_key_to = field.related_model
      if field_type == 'Char':
        max_length = field.max_length
      if field_type not in TYPES:
        raise Exception(
            'I am not familiar with the {} type'.format(field_type))

    fields.append(APIField(
        name, help_text, can_filter, field_type, foreign_key_to, max_length,
        required, editable))
  return fields
