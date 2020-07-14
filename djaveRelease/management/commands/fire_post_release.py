from djaveRelease.signals import post_release
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  help = (
      'Fire off the post_release signal so apps can do one time custom '
      'database stuff')

  def handle(self, *args, **options):
    post_release.send(sender=None)
