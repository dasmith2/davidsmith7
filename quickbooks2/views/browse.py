from django.shortcuts import render, get_object_or_404
from djaveClassMagic.instance_to_html import instance_to_html
from djaveClassMagic.find_models import all_models
from djaveLogin.login_required import login_required

from quickbooks2.list_url import list_url
from quickbooks2.quickbooks_model_from_name import quickbooks_model_from_name
from quickbooks2.views.nav import qb2_nav_context
from quickbooks2.widgets.quickbooks_objects import QuickbooksObjects


def list_widget_for_model(model):
  for widget_class in all_models(subclass_of=QuickbooksObjects):
    if widget_class.get_model() is model:
      return widget_class()
  raise Exception((
      'I was unable to find a subclass of QuickbooksObjects whose '
      'model is {}').format(model))


@login_required
def quickbooks2_model_list(request, model_name):
  model = quickbooks_model_from_name(model_name)

  context = qb2_nav_context(
      list_url(model_name),
      the_one_thing_on_this_page=list_widget_for_model(model))
  return render(request, 'qb2_base.html', context)


@login_required
def quickbooks2_model_instance(request, model_name, pk):
  model = quickbooks_model_from_name(model_name)

  instance = get_object_or_404(model.allowed_by_user(request.user), pk=pk)

  context = qb2_nav_context(
      list_url(model_name),
      the_one_thing_on_this_page=instance_to_html(instance))
  return render(request, 'qb2_base.html', context)
