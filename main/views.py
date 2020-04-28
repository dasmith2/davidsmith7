from django.shortcuts import render


def this_site_js(request):
  return render(request, 'js/this_site.js', content_type='text/javascript')
