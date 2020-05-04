from django.db import models


class WorkType(models.Model):
  name = models.CharField(max_length=400)

  def __repr__(self):
    return '<WorkType {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
