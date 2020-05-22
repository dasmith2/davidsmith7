"""
The manager of any class that wants to periodically delete everything over
a month old should inherit from RmOldManager. The class itself should have a
created datetime field.

Then when you call djaveClass.rm_old.rm_old it'll rm_old from your new class
now too.
"""
from datetime import timedelta

from django.db import models
from djaveDT import now


class RmOldManager(models.Manager):
  def keep_for_days(self):
    return 60

  def rm_old(self, days_ago=None, verbose=False):
    days_ago = days_ago or self.keep_for_days()
    when = now() - timedelta(days=days_ago)
    which = self.filter(created__lt=when)
    if verbose:
      print('Deleting {} {}.'.format(which.count(), str(self.model)))
    which.delete()
