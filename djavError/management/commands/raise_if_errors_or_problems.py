from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import reverse

from djavError.models.fixable import get_fixables
from djavError.models import (
    Error, LongRequest, Notification, TooManyQueriesRequest)


class Command(BaseCommand):
  def handle(self, *args, **options):
    for klass in [Error, LongRequest, Notification, TooManyQueriesRequest]:
      fixables_count = get_fixables(klass).count()
      if fixables_count:
        url = '{}{}'.format(settings.THIS_SERVERS_BASE_URL, reverse('errors'))
        message = (
            'The local database has {} count: {}. Investigate at {}').format(
                klass.__name__, fixables_count, url)
        raise Exception(message)
