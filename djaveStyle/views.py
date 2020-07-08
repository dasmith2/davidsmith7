from django.shortcuts import render
from djaveStyle.models import get_zoom_override


def css(request, template_file_name):
  context = {'override_zoom_factor': get_zoom_override(request.user)}
  return render(
      request, 'css/{}'.format(template_file_name), context=context,
      content_type='text/css')
