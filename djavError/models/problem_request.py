from django.db import models
from djaveDT import now


class ProblemRequest(models.Model):
  path = models.CharField(max_length=300)
  method = models.CharField(max_length=10)
  variables = models.TextField(
      help_text='request.POST or request.GET, depending on the method')
  created = models.DateTimeField(auto_now_add=True)
  latest = models.DateTimeField()
  count = models.PositiveIntegerField(default=1)

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
