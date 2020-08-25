from djaveAPI.problem import Problem


def get_instance(model_name, manager, pk, credentials):
  instance = manager.filter(pk=pk).first()
  if not instance:
    raise Problem('{} {} does not exist'.format(model_name, pk), 404)
  if hasattr(instance, 'as_child_class'):
    instance = instance.as_child_class()
  if not credentials.allowed_instance(instance):
    raise Problem('You do not have permission to manage this {}'.format(
        model_name))
  return instance
