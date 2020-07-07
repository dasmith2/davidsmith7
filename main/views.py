from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js
from main.templatetags.zoom import zoom_by_request


def all_sites_js(request):
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context={'ajax_js': ajax_js()})


def this_site_js(request):
  return render(request, 'js/this_site.js', content_type='text/javascript')


def css(request, template_file_name):
  context = {'font_size': zoom_by_request(request, 20)}
  return render(
      request, 'css/{}'.format(template_file_name), context=context,
      content_type='text/css')
