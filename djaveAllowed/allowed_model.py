from djaveAllowed.credentials import HasUserCredentialsInterface


class AllowedModel(object):
  """ A mixin you can put on your models that says what functions you should
  define in order for other code to be able to check permissions. """

  @classmethod
  def allowed_by_credentials(cls, credentials):
    """ Return a list of objects that the given credentials are allowed to see.
    Well, not a list exactly, a query set.

    Let's say you have a Car model where every car has an owner. Now let's
    say you create Owner level API keys. OK so if you call
    Car.allowed_by_credentials(bobs_api_key) you probably want it to
    return Car.all.filter(owner=Bob)

    This function is used all over the place in the API and in AJAX to make
    sure nobody can see or edit any object that they don't actually have access
    to, which is why it has to be a query set. """
    if isinstance(credentials, HasUserCredentialsInterface):
      return cls.allowed_by_user(credentials.user)
    raise NotImplementedError(
        'allowed_by_credentials in {} does not know how to handle {}'.format(
            cls, credentials.__class__))

  @classmethod
  def allowed_by_user(cls, user):
    """ Return a list of objects that the user is allowed to see. Well, not
    a list exactly, a query set. """
    raise NotImplementedError('allowed_by_user {}'.format(cls))

  @classmethod
  def allowed_by_user_live(cls, user):
    """ Same exact thing as allowed_by_user, except only include intances that
    haven't been deleted or anything. This is useful for the web, where all
    "deleted" objects should remain hidden. """
    raise NotImplementedError('allowed_by_user_live {}'.format(cls))

  def explain_why_invalid(self):
    """ If you have anything more complicated than required fields in your
    class, you'll want to override this function to prevent bad data coming in
    through the API, and to prevent users from updating objects via AJAX to bad
    values. """
    return
