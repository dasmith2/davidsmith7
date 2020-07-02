from django.conf import settings
from django.shortcuts import render
from djaveClassMagic.signals import do_destroy_user


def demo_done(request):
  if not settings.LOCAL:
    raise Exception(
        'This view destroys the current user which is obviously very '
        'dangerous, so this view only works locally')
  if request.user.is_authenticated:
    do_destroy_user(request.user)
  return render(request, 'demo_done.html')
