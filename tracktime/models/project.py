from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable
from djaveClassMagic.signals import destroy_user


@receiver(destroy_user, sender=User)
def destroy_user_projects(sender, destroy_object=None, **kwargs):
  for project in Project.objects.filter(creator=destroy_object):
    destroy_user.send(sender=Project, destroy_object=project)
    project.destroy()


class Project(Publishable):
  """ Users track time against Projects. A """
  name = models.CharField(max_length=400, help_text=(
      'What is this Project called?'))
  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this Project created?'))
  creator = models.ForeignKey(User, on_delete=models.PROTECT, help_text=(
      'Who created this Project?'))

  @classmethod
  def model_description(cls):
    return 'Users track time against Projects.'

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)

  def explain_why_invalid(self):
    if Project.objects.filter(
        ~Q(pk=self.pk), creator=self.creator, name=self.name).exists():
      return 'You already have a Project with this name'

  def __repr__(self):
    return '<Project {}: {}>'.format(self.pk, self.name)

  def __str__(self):
    return self.name
