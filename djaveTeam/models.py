from django.contrib.auth.models import User
from django.db import models
from djaveAPI.publishable import Publishable
from djaveAPI.models.api_key import APIKey, APIKeyManager


class Team(Publishable):
  name = models.CharField(max_length=200)


class TeamMember(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  team = models.ForeignKey(Team, on_delete=models.CASCADE)

  class Meta:
    unique_together = ['user', 'team']


class TeamAPIKeyManager(APIKeyManager):
  def create_key(self, team, name):
    return super().create_key(name, team=team)

  def get_team(self, username, plain_password):
    api_key = self.get_api_key(username, plain_password)
    if api_key:
      return api_key.team


class TeamAPIKey(APIKey):
  team = models.ForeignKey(Team, on_delete=models.CASCADE)

  objects = TeamAPIKeyManager()
