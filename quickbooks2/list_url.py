from django.db.models import Model
from django.shortcuts import reverse


def list_url(model_or_model_name):
  if isinstance(model_or_model_name, str):
    model_name = model_or_model_name
  elif issubclass(model_or_model_name, Model):
    model_name = model_or_model_name._meta.model_name
  else:
    raise Exception(model_or_model_name)
  return reverse(
      'quickbooks2_model_list', kwargs={'model_name': model_name})
