""" Run rm_old daily. It'll find all your classes with an objects attribute
that's an RmOldManager, and run rm_old on them. """
from djaveClass.find_models import all_models
from djaveClass.rm_old_manager import RmOldManager


def rm_old(verbose=False):
  for cls in find_rm_old_classes():
    cls.objects.rm_old(verbose=verbose)


def find_rm_old_classes():
  rm_old_classes = []
  for cls in all_models():
    if hasattr(cls, 'objects'):
      if isinstance(cls.objects, RmOldManager):
        rm_old_classes.append(cls)
  return rm_old_classes
