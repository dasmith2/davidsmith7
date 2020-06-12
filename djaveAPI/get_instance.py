from djaveAPI.problem import Problem
from djaveAPI.models.pretend_publishable import PretendPublishable


def get_instance(model, pk, credentials):
  instance = None
  try:
    find_with_model = model
    if issubclass(model, PretendPublishable):
      find_with_model = model.actually_publishing()
    instance = credentials.allowed_list(find_with_model).filter(pk=pk).first()
    if issubclass(model, PretendPublishable):
      instance = model(instance)
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise Problem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise Problem((
        'Either there is no {} with id {}, or your credentials '
        'do not have permission to access it.').format(
            model.__name__, pk), 404)
  return instance
