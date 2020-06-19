from django.db import models


class AllowedInterface(object):
  """ An interface you should have under any class that will need to check who
  is allowed to do things to its instances. But if it's a model, use Allowed
  """
  @classmethod
  def filter_live(cls, query_set):
    """ Filter the query_set to only include "live" objects, meaning they
    haven't been deleted or deactivated and they're appropriate for showing in
    the user interface. """
    raise NotImplementedError('filter_live {}'.format(cls))

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    raise NotImplementedError('filter_allowed_by_user {}'.format(cls))

  @classmethod
  def allowed_by_user(cls, user):
    """ Return a list of objects that the user is allowed to see, regardless of
    whether the objects are deleted. Well, not a list exactly, a query set.
    This is useful for the API, which needs to pull back lists of objects that
    a User API Key is allowed to see. """
    return cls.filter_allowed_by_user(user, cls.objects.all())

  @classmethod
  def allowed_by_user_live(cls, user):
    """ Same exact thing as allowed_by_user, except only include intances that
    haven't been deleted or anything. This is useful for the web, where all
    "deleted" objects should remain hidden. """
    return cls.filter_live(cls.allowed_by_user(user))

  def explain_why_invalid(self):
    """ If you need to validate anything more complicated than required fields,
    basic type checking, or who-has-permission-to-see-what, you'll want to
    override this function to prevent bad data coming in through the API, or
    through AJAX, or through the class magic edit table. """
    return


class Allowed(models.Model, AllowedInterface):
  """ A base class you should have under any model that will need to check who
  is allowed to do things to its instances. That especially includes any model
  you want to publish in the API, or any model you want to be able to edit with
  reusable AJAX tools in the web user interface. """

  def save(self, *args, **kwargs):
    why_invalid = self.explain_why_invalid()
    if why_invalid:
      raise Exception(why_invalid)
    super().save(*args, **kwargs)

  class Meta:
    abstract = True
