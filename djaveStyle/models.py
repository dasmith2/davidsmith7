from django.contrib.auth.models import User
from django.db import models
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField


def get_zoom_override(user):
  if user.is_authenticated:
    preference = ZoomPreference.objects.filter(user=user).first()
    if preference:
      return preference.zoom


def set_zoom_override(user, new_value):
  preference = ZoomPreference.objects.filter(user=user).first()
  if not preference:
    preference = ZoomPreference(user=user)
  preference.zoom = new_value
  preference.save()


class ZoomPreference(models.Model):
  user = OneToOneOrNoneField(User, on_delete=models.CASCADE)
  zoom = models.FloatField(default=None, blank=True, null=True, help_text=(
      'If this value is set, use it as a permanent zoom value for this user '
      'as opposed to dynamically calculating the zoom value based purely '
      'on the size of the user\'s screen.'))
