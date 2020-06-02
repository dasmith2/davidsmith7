from djaveAPI.signals import publishable_post_save


class PretendPublishable(object):
  def __init__(self, instance=None):
    self.instance = instance or self.__class__.new_instance()

  @classmethod
  def new_instance(cls):
    raise NotImplementedError('new_instance')

  def delete(self):
    raise Exception(
        'If you actually delete a record and the consumer misses the '
        'webhook, how will they ever find out it was deleted? Use '
        'mark_deleted instead.')

  def explain_why_invalid(self):
    return

  def __setattr__(self, name, value):
    if name in self.field_names():
      self.instance.__setattr__(name, value)
    else:
      super().__setattr__(name, value)

  def __getattr__(self, name):
    if name in self.field_names():
      return getattr(self.instance, name)
    return super().__getattr__(name)

  def field_names(self):
    return [f.name for f in self.__class__.get_model_fields_for_api()]

  def save(self):
    self.instance.save()
    publishable_post_save(sender=self.__class__, instance=self)

  def published_object(self):
    return self.instance

  def mark_deleted(self, nnow=None):
    raise NotImplementedError('mark_deleted')

  @classmethod
  def get_model_fields_for_api(cls):
    raise NotImplementedError('get_model_fields_for_api')

  @classmethod
  def allowed(cls, api_key):
    """ Return a query set that will only retrieve instances the given api_key
    is allowed to see. """
    raise NotImplementedError('allowed')

  def allowed_api_keys(self, api_key_type):
    """ Return a list of API Keys of the given type with permission to this
    object. This is how we figure out what webhooks we need to send. """
    raise NotImplementedError('allowed_api_keys')
