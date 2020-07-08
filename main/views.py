from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js


def all_sites_js(request):
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context={'ajax_js': ajax_js()})
