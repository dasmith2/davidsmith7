from django.shortcuts import reverse
from django.template.loader import render_to_string


def ajax_js():
  context = {'update_field_url': reverse('update_field')}
  return render_to_string('ajax.js', context)
