from django.shortcuts import render, reverse
from django.conf import settings
from djaveNav.nav import NavItem, Nav
from djaveLogin.login_required import login_required
from djaveS3.public_file_url import public_file_url_root
from djaveS3.views import sensitive_file_response

from biscuits.models import PrivateBiscuit, PublicBiscuit


@login_required
def private_biscuits(request):
  if request.method == 'POST':
    PrivateBiscuit.objects.create(file_name=request.POST['file_name'])
  context = biscuit_context(
      'private_biscuits', settings.PRIVATE_BUCKET,
      PrivateBiscuit.objects.all())
  return render(request, 'private_biscuits.html', context)


@login_required
def public_biscuits(request):
  if request.method == 'POST':
    PublicBiscuit.objects.create(file_name=request.POST['file_name'])
  context = biscuit_context(
      'public_biscuits', settings.PUBLIC_BUCKET,
      PublicBiscuit.objects.all())
  context['public_biscuit_photo_url_root'] = public_file_url_root(
      settings.PUBLIC_BUCKET)
  return render(request, 'public_biscuits.html', context)


@login_required
def view_private_biscuit(request, file_name):
  return sensitive_file_response(PrivateBiscuit.objects.get(
      file_name=file_name))


def biscuit_context(current_view_name, bucket, biscuits):
  nav_list = [
      NavItem('public_biscuits', 'Public biscuits'),
      NavItem('private_biscuits', 'Private biscuits')]
  return {
      'nav': Nav(nav_list, current_view_name),
      'bucket': bucket,
      'biscuits': biscuits,
      'save_biscuit_url': reverse(current_view_name)}
