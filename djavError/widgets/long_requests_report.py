from djavError.models.long_request import LongRequest
from djavError.widgets.fixable_report import FixableReport
from djavError.widgets.problem_requests_table import ProblemRequestsTable


class LongRequestsReport(FixableReport):
  def get_table(self):
    return LongRequestsTable(
        self.from_date(), self.to_date(),
        self.status_filter.get_value_or_default())


class LongRequestsTable(ProblemRequestsTable):
  def get_model(self):
    return LongRequest

  def headers(self):
    return super().headers() + ['Avg sec']

  def get_cells(self, long_request):
    return super().get_cells(long_request) + [long_request.average_duration()]
