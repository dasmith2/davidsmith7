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
    return self.created_at + timedelta(hours=1)

  class Meta:
    abstract = True


class PublicBiscuit(Biscuit):
  def bucket_config(self):
    return settings.PUBLIC_BUCKET


class PrivateBiscuit(Biscuit):
  def bucket_config(self):
    return settings.PRIVATE_BUCKET
