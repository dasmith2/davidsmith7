from django.shortcuts import render
from djaveAPI.ajax_js import ajax_js
from djaveClassMagic.edit_list_table import edit_list_table_js


def all_sites_js(request):
  context = {
      'ajax_js': ajax_js(),
      'edit_list_table_js': edit_list_table_js()}
  return render(
      request, 'js/all_sites.js', content_type='text/javascript',
      context=context)
