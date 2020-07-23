from djavError.models.long_request import LongRequest
from djavError.tests.models.test_problem_request import (
    set_problem_request_stuff)


def get_test_long_request(**kwargs):
  instance = LongRequest(
      total_duration=kwargs.get('total_duration', 10))
  return set_problem_request_stuff(instance, **kwargs)
