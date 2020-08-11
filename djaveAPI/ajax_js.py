from django.shortcuts import reverse
from django.template.loader import render_to_string


def ajax_js():
  context = {'api_root_url': reverse('api_root')}
  return render_to_string('ajax.js', context)
