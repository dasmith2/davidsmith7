from datetime import timedelta

from django.shortcuts import reverse
from djaveDT import now
from django.conf import settings
from djaveS3.models.photo import Photo


class Biscuit(Photo):
  def explain_why_can_delete(self, nnow=None):
    nnow = nnow or now()
    if nnow > self.get_keep_until():
      return 'We only keep these for an hour.'

  def calc_and_set_keep(self):
    self.keep_until = self.get_keep_until()

  def get_keep_until(self):
    return self.created + timedelta(hours=1)

  class Meta:
    abstract = True


class PublicBiscuit(Biscuit):
  def src(self):
    return self.public_file_url()

  def bucket_config(self):
    return settings.PUBLIC_BUCKET


class PrivateBiscuit(Biscuit):
  def src(self):
    return reverse(
        'view_private_biscuit', kwargs={'file_name': self.file_name})

  def bucket_config(self):
    return settings.PRIVATE_BUCKET
