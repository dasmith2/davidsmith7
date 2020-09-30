from djaveAPI.problem import Problem


def get_instance(manager, pk, credentials):
  model_name = manager.model.__name__
  instance = manager.filter(pk=pk).first()
  if not instance:
    raise Problem('{} {} does not exist'.format(model_name, pk), 404)
  if hasattr(instance, 'as_child_class'):
    instance = instance.as_child_class()
  if not credentials.allowed_instance(instance):
    raise Problem('You do not have permission to manage this {}'.format(
        model_name), 403)
  return instance
