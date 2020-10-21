from django.conf import settings
from django.http import HttpResponse


def qb_authorize_callback(request):
  """
  settings.QUICKBOOKS_CLIENT_ID, settings.QUICKBOOKS_CLIENT_SECRET
  """
  return HttpResponse('Hello!')
