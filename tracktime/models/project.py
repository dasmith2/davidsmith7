from django.db import models


class Project(models.Model):
  name = models.CharField(max_length=400)
  created = models.DateTimeField(auto_now_add=True)

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
