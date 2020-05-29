""" Functions for locating models. """
from importlib import import_module

from django.conf import settings
from django.db.models import Model


def model_from_name(model_name):
  """ Given just the name of the model, return the model itself. The point is
  not to have to also specify an app. """
  for model in all_models():
    if model.__name__ == model_name:
      return model


def all_models(subclass_of=None):
  """ By default this returns all Django models. But you can have it return a
  list of all classes that subclass anything, as long as those classes are
  directly in the models module of Django apps. """
  to_return = []
  for app_name in settings.INSTALLED_APPS:
    to_return.extend(models_in_app(app_name, subclass_of=subclass_of))
  return to_return


def models_in_app(app_name, subclass_of=None):
  subclass_of = subclass_of or Model
  to_return = []
  module = import_module(app_name)
  if hasattr(module, 'models'):
    for model_name, cls in module.models.__dict__.items():
      if isinstance(cls, type) and issubclass(cls, subclass_of):
        to_return.append(cls)
  return to_return
