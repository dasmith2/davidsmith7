from abc import abstractmethod

from django.db import models
from djaveDT import now


class PublishedManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=True)


class DeletedManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=False)


class Published(models.Model):
  """ Have your models inherit from this class if you want your models to be
  published online as part of a REST-ish API. """
  deleted = models.DateTimeField(blank=True, null=True)

  def mark_deleted(self, nnow=None):
    nnow = nnow or now()
    self.deleted = nnow
    self.save()

  def delete(self):
    raise Exception(
        'If you actually delete a record and the consumer misses the '
        'webhook, how will they ever find out it was deleted? Use '
        'mark_deleted instead.')

  @abstractmethod
  def as_json(self):
    raise NotImplementedError('as_json')

  live = PublishedManager()
  all = models.Manager()

  class Meta:
    abstract = True
