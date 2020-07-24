from django.db import models
from djaveDT import now
from djavError.models.fixable import Fixable


class ProblemRequest(Fixable):
  path = models.CharField(max_length=300)
  method = models.CharField(max_length=10)
  variables = models.TextField(
      null=True, blank=True,
      help_text='request.POST or request.GET, depending on the method')

  def increment(self):
    self.count += 1
    self.latest = now()
    self.save()

  def save(self, *args, **kwargs):
    if not self.latest:
      self.latest = now()
    super().save(*args, **kwargs)

  class Meta:
    abstract = True
