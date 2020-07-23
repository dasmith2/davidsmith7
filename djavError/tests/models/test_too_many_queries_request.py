from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.tests.models.test_problem_request import (
    set_problem_request_stuff)


def get_test_too_many_queries_request(**kwargs):
  instance = TooManyQueriesRequest(
      total_query_count=kwargs.get('total_query_count', 20))
  return set_problem_request_stuff(instance, **kwargs)
