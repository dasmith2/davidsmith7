from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
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
  def allowed_by_user(cls, user):
    return cls.all.filter(creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)
    raise Exception('I dont know how to check which {} can see this Project')

  def explain_why_invalid(self):
    if Project.all.filter(
        ~Q(pk=self.pk), creator=self.creator, name=self.name).exists():
      return 'You already have a project with this name'

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
