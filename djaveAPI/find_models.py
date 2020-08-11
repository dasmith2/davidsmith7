""" Dig through all the models and calculate the API schema, which will inform
the documentation and the API itself. """

from django.conf import settings
from djaveAllowed.models import AllowedInterface
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveClassMagic.find_models import models_in_app


def use_model_instance_for_api(instance, allowed_class=None):
  """ Returns a (model, instance) tuple. The entire point of this is wiring
  Django's user model into the API. """
  model = instance.__class__
  if allowed_class:
    model = allowed_class
    if issubclass(model, PretendPublishable) and not isinstance(
        instance, PretendPublishable):
      instance = model(instance)
  return model, instance


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
  if issubclass(model, (PretendPublishable, Publishable)):
    return model
  raise Exception(
      '{} is not a PretendPublishable or Publishable'.format(model_name))
