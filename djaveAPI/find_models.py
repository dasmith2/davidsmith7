""" Dig through all the models and calculate the API schema, which will inform
the documentation and the API itself. """

from django.conf import settings
from djaveAllowed.models import AllowedInterface
from djaveAPI.models.publishable import Publishable
from djaveClassMagic.find_models import models_in_app


def allowed_models():
  to_return = []
  for app_name in settings.INSTALLED_APPS:
    to_return.extend(allowed_models_in_app(app_name))
  return to_return


def allowed_models_in_app(app_name):
  return models_in_app(app_name, AllowedInterface)


def allowed_model_from_name(model_name):
  for model in allowed_models():
    if model.__name__ == model_name:
      return model
  raise Exception('Unable to find {}'.format(model_name))


def publishable_model_from_name(model_name):
  model = allowed_model_from_name(model_name)
  if issubclass(model, Publishable):
    return model
  raise Exception('{} is not a Publishable'.format(model_name))
