""" Run rm_old daily. It'll find all your classes with an objects attribute
that's an RmOldManager, and run rm_old on them. """
from importlib import import_module

from django.conf import settings
from djaveClass.rm_old_manager import RmOldManager


def rm_old(verbose=False):
  for cls in find_rm_old_classes():
    cls.objects.rm_old(verbose=verbose)


def find_rm_old_classes():
  rm_old_classes = []
  for app_name in settings.INSTALLED_APPS:
    module = import_module(app_name)
    if hasattr(module, 'models'):
      for model_name, cls in module.models.__dict__.items():
        if isinstance(cls, type):
          if hasattr(cls, 'objects'):
            if isinstance(cls.objects, RmOldManager):
              rm_old_classes.append(cls)
  return rm_old_classes
