from django.db import models
from djavError.models.problem_request import ProblemRequest


class TooManyQueriesRequest(ProblemRequest):
  total_query_count = models.PositiveIntegerField(help_text=(
      'How many database queries happened in these requests?'))

  def increment(self, query_count):
    self.total_query_count += query_count
    super().increment()

  def average_query_count(self):
    return self.total_query_count / self.count
