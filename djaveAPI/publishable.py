from django.db import models
from djaveDT import now


class PublishableManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=True)


class DeletedManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=False)


class Publishable(models.Model):
  """ Have your models inherit from this class if you want your models to be
  published online as part of a REST-ish API. """
  deleted = models.DateTimeField(blank=True, null=True, help_text=(
      'When was this object "deleted"? Deleted objects '
      'should basically be ignored. By simply marking objects as deleted '
      'instead of actually deleting them, I make it much simpler for you to '
      'write code that notices when objects in the API become deleted.'))

  def mark_deleted(self, nnow=None):
    nnow = nnow or now()
    self.deleted = nnow
    self.save()

  def delete(self):
    raise Exception(
        'If you actually delete a record and the consumer misses the '
        'webhook, how will they ever find out it was deleted? Use '
        'mark_deleted instead.')

  live = PublishableManager()
  all = models.Manager()

  class Meta:
    abstract = True
