from djaveCRUDTable.columns import DisplayFieldColumn

from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.widgets.problem_requests import ProblemRequests


class TooManyQueriesRequests(ProblemRequests):
  def get_model(self):
    return TooManyQueriesRequest

  def get_tail_columns(self):
    return super().get_tail_columns() + [
        DisplayFieldColumn('Avg query count', 'average_query_count')]
