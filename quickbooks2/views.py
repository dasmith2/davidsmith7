from django.http import HttpResponse


def qb_authorize_callback(request):
  return HttpResponse('Hello!')
