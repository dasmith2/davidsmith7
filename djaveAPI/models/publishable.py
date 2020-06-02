from django.db import models
from djaveAPI.signals import publishable_post_save
from djaveDT import now


class PublishableManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=True)


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

  def explain_why_invalid(self):
    """ If you have anything more complicated than required fields in your
    class, you'll want to override this function to prevent bad data coming in
    through the API. """
    return

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
  def get_model_fields_for_api(cls):
    return cls._meta.get_fields()

  @classmethod
  def allowed(cls, api_key):
    """ Return a query set that will only retrieve instances the given api_key
    is allowed to see. """
    raise NotImplementedError('allowed {}'.format(cls))

  def allowed_api_keys(self, api_key_type):
    raise NotImplementedError('allowed_api_keys {}'.format(self.__class__))

  live = PublishableManager()
  all = models.Manager()

  class Meta:
    abstract = True
