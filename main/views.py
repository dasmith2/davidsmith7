from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js


def all_sites_js(request):
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context={'ajax_js': ajax_js()})


def this_site_js(request):
  return render(request, 'js/this_site.js', content_type='text/javascript')


def all_sites_css(request):
  return render(request, 'css/all_sites.css', content_type='text/css')


def this_site_css(request):
  return render(request, 'css/this_site.css', content_type='text/css')
