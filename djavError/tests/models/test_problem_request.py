from djavError.tests.models.test_fixable import set_fixable_stuff


def set_problem_request_stuff(instance, **kwargs):
  instance.path = kwargs.get('path', '/tt')
  instance.method = kwargs.get('method', 'GET')
  instance.variables = kwargs.get('variables', '{}')
  return set_fixable_stuff(instance, **kwargs)
