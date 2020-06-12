class CredentialsInterface(object):
  """ This could represent an API Key or a logged in User. """

  def allowed_instance(self, instance):
    """ Does this API Key or User or whatever have permission to instance? """
    return self.allowed_list(instance.__class__).filter(
        pk=instance.pk).exists()

  def allowed_list(self, model):
    """ Return a query set that will return a list of `model` such that these
    credentials have permission to every instance. """
    raise NotImplementedError('allowed_list {}'.format(self.__class__))

  def explain_why_can_not_create(self, model):
    """ Return an explanation, if any, for why these credentials are unable to
    create instances of the given model. """
    raise NotImplementedError(
        'explain_why_can_not_create {}'.format(self.__class__))


class HasUserCredentialsInterface(CredentialsInterface):
  """ If your object simply has a user property and that's what we're checking
  permission with, just have your object inherit from
  HasUserCredentialsInterface instead of CredentialsInterface, which will come
  in handy if I ever make API keys on a level other than User. """
  def allowed_list(self, model):
    if hasattr(model, 'allowed_by_user'):
      return model.allowed_by_user(self.user)
    raise Exception((
        'I do not know how to return a list of {} that a user has '
        'permission to').format(model))


class UserCredentials(HasUserCredentialsInterface):
  def __init__(self, user):
    self.user = user
