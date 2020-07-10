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

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    if user.is_superuser:
      return query_set
    return query_set.none()
