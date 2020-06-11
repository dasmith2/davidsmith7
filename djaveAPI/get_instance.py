from djaveAPI.problem import Problem


def get_instance(model, pk, credentials):
  instance = None
  try:
    instance = credentials.allowed_list(model).filter(pk=pk).first()
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise Problem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise Problem((
        'Either there is no {} with id {}, or this API '
        'Key does not have permission to access it.').format(
            model.__name__, pk), 404)
  return instance
