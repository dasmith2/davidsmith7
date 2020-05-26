from django.contrib.auth.models import User
from django.db import models
from djaveAPI.publishable import Publishable


class Project(Publishable):
  """ Users track time against Projects. A """
  name = models.CharField(max_length=400, help_text=(
      'What is this project called?'))
  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this project created?'))
  creator = models.ForeignKey(User, on_delete=models.PROTECT, help_text=(
      'Who created this project?'))

  def model_description():
    return 'Users track time against Projects.'

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
