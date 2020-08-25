""" Turn an object into JSON suitable for publishing in an API. """
from djaveAPI.currency_field import corresponding_currency_field_name
from djaveClassMagic.model_fields import (
    model_fields, django_primary_key_field, DATE_TIME, DATE)
from djmoney.money import Money


TYPE = 'type'


def to_json_dict(instance, allowed_class=None):
  model = instance.__class__

  as_dict = {TYPE: model.__name__}
  for field in model_fields(model):
    use_field_name = field.name
    value = None
    if field.foreign_key_to:
      value = getattr(instance, '{}_id'.format(field.name))
    elif field.name == 'id':
      dj_pk_field = django_primary_key_field(instance.__class__)
      if dj_pk_field.name == 'id':
        # Normal situation.
        value = instance.id
      elif dj_pk_field.related_model:
        # The primary key is a one to one foreign key.
        value = getattr(instance, dj_pk_field.name).id
      else:
        raise Exception(
            'I don\'t know how to get the id from {}'.format(instance))
    else:
      value = getattr(instance, field.name)
      if value is not None:
        if field.type in [DATE_TIME, DATE]:
          value = value.isoformat()
      if isinstance(value, Money):
        currency = value.currency.code
        value = float(value.amount)
        as_dict[corresponding_currency_field_name(field)] = currency
    as_dict[use_field_name] = value
  if hasattr(instance, 'add_to_json'):
    instance.add_to_json(as_dict)
  return as_dict
