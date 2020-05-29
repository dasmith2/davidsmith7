""" Turn an object into JSON suitable for publishing in an API. """
from djaveAPI.discover_schema import (
    api_fields, use_publishable, DATE_TIME, DATE)


TYPE = 'type'


def to_json_dict(instance, publishable_class=None):
  model, instance = use_publishable(
      instance, publishable_class=publishable_class)

  as_dict = {TYPE: model.__name__}
  for field in api_fields(model):
    value = None
    if field.foreign_key_to:
      value = getattr(instance, '{}_id'.format(field.name))
    else:
      value = getattr(instance, field.name)
      if value is not None:
        if field.type in [DATE_TIME, DATE]:
          value = value.isoformat()
    as_dict[field.name] = value
  return as_dict
