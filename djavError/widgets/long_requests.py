from djaveCRUDTable.columns import DisplayFieldColumn

from djavError.models.long_request import LongRequest
from djavError.widgets.problem_requests import ProblemRequests


class LongRequests(ProblemRequests):
  def get_model(self):
    return LongRequest

  def get_tail_columns(self):
    return super().get_tail_columns() + [
        DisplayFieldColumn('Avg sec', 'avg_sec')]
