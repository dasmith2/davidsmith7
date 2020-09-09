from django.conf import settings
from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js


def all_sites_js(request):
  context = {
      'ajax_js': ajax_js(),
      'in_web_test': settings.WEB_TEST}
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context=context)
