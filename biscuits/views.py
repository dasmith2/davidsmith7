from django.shortcuts import render
from djaveNav.nav import NavItem, Nav


def private_biscuits(request):
  return render(request, 'private_biscuits.html', biscuit_context(
      'private_biscuits'))


def public_biscuits(request):
  return render(request, 'public_biscuits.html', biscuit_context(
      'public_biscuits'))


def biscuit_context(current_view_name):
  nav_list = [
      NavItem('private_biscuits', 'Private biscuits'),
      NavItem('public_biscuits', 'Public biscuits')]
  return {'nav': Nav(nav_list, current_view_name)}
