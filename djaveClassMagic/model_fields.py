from collections import namedtuple
import re

from django.db.models import Model
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.reverse_related import ManyToOneRel
from djaveDT import dt_to_str, d_to_str


DATE_TIME = 'DateTime'
DATE = 'Date'
FLOAT = 'Float'
INTEGER = 'Integer'
TEXT = 'Text'
CHAR = 'Char'
BOOLEAN = 'Boolean'
TYPES = [DATE_TIME, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN]


# I would have just inlined this and not had to name it, except flake8.
FIELD_FIELD_LIST = [
    'name', 'display_name', 'help_text', 'can_filter', 'type',
    'foreign_key_to', 'max_length', 'required', 'editable', 'default']


class ModelField(namedtuple('ModelField', FIELD_FIELD_LIST)):
  def value_as_str(self, instance_or_value):
    """ instance_or_value can be either an instance of an object that has this
    field, or it can be a, like, primitive value that's hopefully of the same
    "type" as this ModelField. """
    if isinstance(instance_or_value, Model):
      value = getattr(instance_or_value, self.name)
    else:
      value = instance_or_value

    if value is None:
      return ''

    if self.type == FLOAT:
      return round(value, 2)
    elif self.type in [INTEGER, TEXT, CHAR, BOOLEAN]:
      return value
    elif self.type == DATE_TIME:
      return dt_to_str(value)
    elif self.type == DATE:
      return d_to_str(value)
    else:
      raise Exception(
          'Not sure how to represent a value of type {}'.format(self.type))


def _get_django_model_fields(cls):
  if hasattr(cls, 'get_model_fields'):
    return cls.get_model_fields()
  return cls._meta.get_fields()


def model_fields_lookup(model):
  lookup = {}
  for field in model_fields(model):
    lookup[field.name] = field
  return lookup


def django_primary_key_field(model):
  for field in _get_django_model_fields(model):
    if hasattr(field, 'primary_key') and field.primary_key:
      return field


def model_fields(model, specific_field=None):
  fields = []
  for field in _get_django_model_fields(model):
    name = field.name
    is_ptr_to_base_class = re.compile(r'\w+_ptr').findall(name)
    if is_ptr_to_base_class:
      continue
    if isinstance(field, ManyToOneRel):
      continue
    if 'child_class' == name:
      continue

    can_filter = field.db_index
    help_text = field.help_text
    field_type = field.get_internal_type()
    required = not field.null
    editable = field.editable
    default = field.default
    if default is NOT_PROVIDED:
      default = None
    foreign_key_to = None
    max_length = None

    is_id = field.primary_key
    if is_id:
      # The name is typically already 'id', but not when the primary key is
      # also a OneToOne foreign key.
      name = 'id'
      required = False
      can_filter = False
      editable = False
      help_text = 'What is the primary key for this object?'
      field_type = 'Integer'
    else:
      field_type = field_type.replace('Field', '')
      if field_type in ['ForeignKey', 'OneToOne', 'OneToOneOrNone']:
        try:
          field.get_prep_value(1)
        except ValueError:
          raise Exception(
              'The API doesnt know how to handle non-integer primary keys '
              'yet. See filter_model in djaveAPI.filters specifically')
        field_type = INTEGER
        foreign_key_to = field.related_model
      elif field_type == 'ManyToMany':
        continue
      if field_type == 'PositiveInteger':
        field_type = INTEGER
      if field_type == 'Decimal':
        field_type = FLOAT
      if field_type == CHAR:
        max_length = field.max_length
      if field_type in [CHAR, TEXT] and field.blank:
        required = False
      if field_type not in TYPES:
        raise Exception(
            'I am not familiar with the {} type'.format(field_type))

      if name.find('_currency') > 0:
        required = True
        editable = True
        help_text = '"USD" typically'

    model_field = ModelField(
        name, field.verbose_name.capitalize(), help_text, can_filter,
        field_type, foreign_key_to, max_length, required, editable, default)
    if name == specific_field:
      return model_field
    else:
      fields.append(model_field)
  if specific_field:
    return None
  return fields
