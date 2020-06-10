from datetime import date

from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime, parse_date
from djaveAPI.currency_field import corresponding_currency_value
from djaveAPI.find_models import use_publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.problem import Problem
from djaveClass.model_fields import (
    model_fields, DATE_TIME, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN)
from djaveDT import now
from djmoney.money import Money


def update(instance, request_POST, api_key, publishable_class=None):
  return _set_fields(
      instance, request_POST, api_key, publishable_class=publishable_class)


def save_new(model, request_POST, api_key, publishable_class=None):
  explain_why_not = api_key.explain_why_can_not_create(model)
  if explain_why_not:
    raise Problem(explain_why_not)
  return _set_fields(
      model(), request_POST, api_key, publishable_class=publishable_class)


def delete(instance, publishable_class=None):
  model, instance = use_publishable(
      instance, publishable_class=publishable_class)
  instance.mark_deleted()


def _set_fields(instance, request_POST, api_key, publishable_class=None):
  model, instance = use_publishable(
      instance, publishable_class=publishable_class)

  for field in model_fields(model):
    if not field.editable:
      continue
    value = None
    if field.name in request_POST:
      raw_value = request_POST[field.name]
      if field.foreign_key_to:
        if raw_value:
          value = allowed(field.foreign_key_to, api_key).filter(
              pk=raw_value).first()
          if value is None:
            raise Problem((
                'Either {} {} does not exist, or your API key does not have '
                'access to it').format(
                    field.foreign_key_to.__name__, raw_value))
          if not isinstance(value, field.foreign_key_to):
            raise Exception(
                '{} allowed function should return {}, not {}'.format(
                    field.foreign_key_to, field.foreign_key_to,
                    value.__class__))
      elif field.type in [DATE, DATE_TIME]:
        value = _date_or_date_time(field, raw_value)
      elif field.type in [FLOAT, INTEGER]:
        value = _float_or_integer(field, raw_value)
        currency = corresponding_currency_value(field, request_POST)
        if currency:
          value = Money(value, currency)
      elif field.type in [TEXT, CHAR]:
        if field.max_length and len(raw_value) > field.max_length:
          raise Problem((
              '{} has a maximum length of {}. You sent a string with '
              'length {}').format(
                  field.name, field.max_length, len(raw_value)))
        value = raw_value
      elif field.type == BOOLEAN:
        value = _boolean(field, raw_value)
      else:
        raise Exception(field.type)
    if field.required and value in [None, '']:
      raise Problem('{} is required'.format(field.name))
    setattr(instance, field.name, value)

  why_invalid = instance.explain_why_invalid()
  if why_invalid:
    raise Problem(why_invalid)
  instance.save()

  return instance


def allowed(model, api_key):
  if hasattr(model, 'allowed'):
    return model.allowed(api_key)
  if isinstance(api_key, UserAPIKey) and model is User:
    return User.objects.filter(pk=api_key.user.pk)
  raise Exception(
      'I dont know how to pull back a list of allowed {} by {}'.format(
          model.__name__, api_key.__class__.__name__))


def _date_or_date_time(field, raw_value):
  if raw_value:
    if field.type == DATE:
      value = parse_date(raw_value)
      example = date.today().isoformat()
    elif field.type == DATE_TIME:
      value = parse_datetime(raw_value)
      example = now().isoformat()
    else:
      raise Exception(field.type)
    if not value:
      raise Problem((
          '{} is not a valid {}. I am looking for something more '
          'like {}').format(raw_value, field.type, example))
    return value


def _float_or_integer(field, raw_value):
  if raw_value not in ['', None]:
    try:
      if field.type == FLOAT:
        return float(raw_value)
      elif field.type == INTEGER:
        return int(raw_value)
      else:
        raise Exception(field.type)
    except ValueError:
      raise Problem(
          '{} is not a valid {}'.format(raw_value, field.type))


def _boolean(field, raw_value):
  if raw_value in ['', None]:
    return None
  return raw_value
