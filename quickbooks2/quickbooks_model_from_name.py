from djaveClassMagic.find_models import model_from_name

from quickbooks2.models.quickbooks_object import QuickBooksObject


def quickbooks_model_from_name(model_name):
  return model_from_name(model_name, subclass_of=QuickBooksObject)
