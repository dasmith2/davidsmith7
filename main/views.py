from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js


def all_sites_js(request):
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context={'ajax_js': ajax_js()})


def this_site_js(request):
  return render(request, 'js/this_site.js', content_type='text/javascript')


def css(request, template_file_name):
  return render(
      request, 'css/{}'.format(template_file_name), content_type='text/css')
