class AllowedModel(object):
  """ A base class you should have under any model that will need to check who
  is allowed to do things to its instances. That especially includes any model
  you want to publish in the API, or any model you want to be able to edit with
  reusable AJAX tools in the web user interface. """

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
    """ If you have anything more complicated than required fields in your
    class, you'll want to override this function to prevent bad data coming in
    through the API or through AJAX. """
    return
