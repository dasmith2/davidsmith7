from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable


class Project(Publishable):
  """ Users track time against Projects. A """
  name = models.CharField(max_length=400, help_text=(
      'What is this project called?'))
  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this project created?'))
  creator = models.ForeignKey(User, on_delete=models.PROTECT, help_text=(
      'Who created this project?'))

  @classmethod
  def model_description(cls):
    return 'Users track time against Projects.'

  @classmethod
  def allowed(cls, api_key):
    if isinstance(api_key, UserAPIKey):
      return cls.all.filter(creator=api_key.user)
    else:
      raise Exception(
          'I do not know how to handle {} api keys'.format(api_key.__class__))

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
