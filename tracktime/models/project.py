from django.db import models
from djaveAPI.published import Published


class Project(Published):
  name = models.CharField(max_length=400)
  created = models.DateTimeField(auto_now_add=True)

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
