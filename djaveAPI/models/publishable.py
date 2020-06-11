from django.db import models
from djaveAPI.models.publishable_interface import PublishableInterface
from djaveAPI.signals import publishable_post_save
from djaveDT import now


class PublishableManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=True)


class Publishable(models.Model, PublishableInterface):
  """ Have your models inherit from this class if you want your models to be
  published online as part of a REST-ish API. """

  deleted = models.DateTimeField(blank=True, null=True, help_text=(
      'When was this object "deleted"? Deleted objects '
      'should basically be ignored. By simply marking objects as deleted '
      'instead of actually deleting them, I make it much simpler for you to '
      'write code that notices when objects in the API become deleted.'))

  def delete(self):
    raise Exception(
        'If you actually delete a record and the consumer misses the '
        'webhook, how will they ever find out it was deleted? Use '
        'mark_deleted instead.')

  def mark_deleted(self, nnow=None):
    nnow = nnow or now()
    self.deleted = nnow
    self.save()

  def save(self, *args, **kwargs):
    if self.explain_why_invalid():
      raise Exception(self.explain_why_invalid())
    super().save(*args, **kwargs)
    publishable_post_save.send(sender=self.__class__, instance=self)

  def published_object(self):
    return self

  @classmethod
  def new_instance(cls):
    return cls()

  @classmethod
  def get_model_fields(cls):
    return cls._meta.get_fields()

  @classmethod
  def allowed_by_user_live(cls, user):
    return cls.allowed_by_user(user).filter(deleted__isnull=True)

  live = PublishableManager()
  all = models.Manager()

  class Meta:
    abstract = True
