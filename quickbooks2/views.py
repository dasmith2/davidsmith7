from django.conf import settings
from django.http import HttpResponse


def qb_authorize_callback(request):
  return HttpResponse(
      'QUICKBOOKS_CLIENT_ID: {}<br>QUICKBOOKS_CLIENT_SECRET: {}'.format(
          settings.QUICKBOOKS_CLIENT_ID, settings.QUICKBOOKS_CLIENT_SECRET))
