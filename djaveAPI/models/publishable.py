from django.db import models
from djaveAPI.signals import publishable_post_save
from djaveDT import now


class PublishableManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(deleted__isnull=True)


class Publishable(models.Model):
  """ Have your models inherit from this class if you want your models to be
  published online as part of a REST-ish API. """

  @classmethod
  def allowed(cls, api_key):
    """ Return a list of objects that the api_key is allowed to see. Well, not
    a list exactly, a query set.

    Let's say you have a Car model where every car has an owner. Now let's
    say you create Owner level API keys. OK so if you call
    Car.allowed(bobs_api_key) you probably want it to
    return Car.all.filter(owner=Bob)

    This function is used all over the place in the API to make sure nobody can
    see or edit any object that they don't actually have access to, which is
    why it has to be a query set. """
    raise NotImplementedError('allowed {}'.format(cls))

  def allowed_api_keys(self, api_key_type):
    """ Return a list of api_keys that are allowed to see this particular
    instance. So if you were to call bobs_car.allowed_api_keys(OwnerAPIKey)
    you probably want it to return [bobs_api_key].

    Pretty much the entire point of this function is to look up who we should
    send webhooks to whenever we save a published object. """
    raise NotImplementedError('allowed_api_keys {}'.format(self.__class__))

  def user_allowed(self, user):
    """ Return True if the given user is allowed to modify this instance. This
    is pretty much needed for djaveAPI.views.update_field which is a beautiful
    abstract tool for modifying objects field by field via AJAX, which makes it
    easy to create fully editable tables of information. """
    raise NotImplementedError('user_allowed {}'.format(self.__class__))

  def explain_why_invalid(self):
    """ If you have anything more complicated than required fields in your
    class, you'll want to override this function to prevent bad data coming in
    through the API, and to prevent users from updating objects via AJAX to bad
    values. """
    return

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

  live = PublishableManager()
  all = models.Manager()

  class Meta:
    abstract = True
