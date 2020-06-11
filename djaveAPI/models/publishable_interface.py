from djaveAPI.models.user_api_key import UserAPIKey


class PublishableInterface(object):
  """ PretendPublishable and Publishable need to be different base classes. """

  @classmethod
  def allowed_by_key(cls, api_key):
    """ Return a list of objects that the api_key is allowed to see. Well, not
    a list exactly, a query set.

    Let's say you have a Car model where every car has an owner. Now let's
    say you create Owner level API keys. OK so if you call
    Car.allowed_by_key(bobs_api_key) you probably want it to
    return Car.all.filter(owner=Bob)

    This function is used all over the place in the API to make sure nobody can
    see or edit any object that they don't actually have access to, which is
    why it has to be a query set. """
    if isinstance(api_key, UserAPIKey):
      return cls.allowed_by_user(api_key.user)
    raise NotImplementedError(
        'allowed_by_key in {} does not know how to handle {}'.format(
            cls, api_key.__class__))

  @classmethod
  def allowed_by_user(cls, user):
    """ Return a list of objects that the user is allowed to see. Well, not
    a list exactly, a query set. """
    raise NotImplementedError('allowed_by_user {}'.format(cls))

  @classmethod
  def allowed_by_user_live(cls, user):
    """ Same exact thing as allowed_by_user, except only include intances that
    haven't been deleted or anything. """
    raise NotImplementedError('allowed_by_user_live {}'.format(cls))

  def allowed_api_keys(self, api_key_type):
    """ Return a list of api_keys that are allowed to see this particular
    instance. So if you were to call bobs_car.allowed_api_keys(OwnerAPIKey)
    you probably want it to return [bobs_api_key].

    Pretty much the entire point of this function is to look up who we should
    send webhooks to whenever we save a published object. """
    raise NotImplementedError('allowed_api_keys {}'.format(self.__class__))

  def explain_why_invalid(self):
    """ If you have anything more complicated than required fields in your
    class, you'll want to override this function to prevent bad data coming in
    through the API, and to prevent users from updating objects via AJAX to bad
    values. """
    return

  @classmethod
  def get_model_fields(cls):
    raise NotImplementedError('get_model_fields')

  def mark_deleted(self, nnow=None):
    raise NotImplementedError('mark_deleted')

  def published_object(self):
    """ What is the actual, like, Django model object instance that this here
    instance is really refering too. In the case of Publishable, it's just
    itself. It's only more complicated with PretendPublishable. """
    raise NotImplementedError('published_object')

  @classmethod
  def new_instance(cls):
    raise NotImplementedError('new_instance')
