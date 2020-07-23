from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.widgets.fixable_report import FixableReport
from djavError.widgets.problem_requests_table import ProblemRequestsTable


class TooManyQueriesRequestsReport(FixableReport):
  def get_table(self):
    return TooManyQueriesRequestsTable(
        self.from_date(), self.to_date(),
        self.status_filter.get_value_or_default())


class TooManyQueriesRequestsTable(ProblemRequestsTable):
  def get_model(self):
    return TooManyQueriesRequest

  def headers(self):
    return super().headers() + ['Avg query count']

  def get_cells(self, too_many_queries_request):
    return super().get_cells(too_many_queries_request) + [
        too_many_queries_request.average_query_count()]
