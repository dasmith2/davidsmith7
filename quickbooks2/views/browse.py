from django.shortcuts import render, get_object_or_404, reverse
from djaveClassMagic.instance_to_html import instance_to_html
from djaveClassMagic.find_models import all_models
from djaveHTML.a import A
from djaveHTML.button import Button
from djaveHTML.problem import Problem
from djaveHTML.wrapper import Wrapper
from djaveLogin.login_required import login_required
from djaveURL import protocol_and_host

from quickbooks2.list_url import list_url
from quickbooks2.models.quickbooks_object import NestedListQuickBooksObject
from quickbooks2.quickbooks_model_from_name import quickbooks_model_from_name
from quickbooks2.views.nav import qb2_nav_context
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


def list_widget_class_for_model(model):
  for widget_class in all_models(subclass_of=QuickBooksObjects):
    if widget_class.get_model() is model:
      return widget_class
  raise Exception((
      'I was unable to find a widget, subclass of QuickBooksObjects '
      '(note the s), whose model is {}. Did you add it to '
      'quickbooks2.widgets.__init__?').format(model))


@login_required
def quickbooks2_model_list(request, model_name):
  model = quickbooks_model_from_name(model_name)

  refresh_button = Button('Pull from QuickBooks', button_type='submit')
  feedback = None
  if refresh_button.get_was_clicked(request.POST):
    user_credentials = request.user.usercredentials_or_none
    auth_stuff = A(
        'authorize us on QuickBooks', reverse('auth_stuff')).as_html()
    if not user_credentials:
      feedback = Problem('Can you please {} first?'.format(auth_stuff))
    elif not user_credentials.refresh_token:
      feedback = Problem('Can you please re-{}?'.format(auth_stuff))
    else:
      model.merge_all(request.user, protocol_and_host(request))

  context = qb2_nav_context(
      list_url(model_name),
      list_widget=list_widget_class_for_model(model)(),
      refresh_button=refresh_button,
      feedback=feedback)
  return render(request, 'quickbooks2_model_list.html', context)


@login_required
def quickbooks2_model_instance(request, model_name, pk):
  model = quickbooks_model_from_name(model_name)

  instance = get_object_or_404(model.allowed_by_user(request.user), pk=pk)

  wrapper = Wrapper(instance_to_html(instance))

  current_url = request.path
  for nested_model in all_models(NestedListQuickBooksObject):
    if nested_model.nested_under_model() is model:
      # For instance, wrapper.add(Lines(current_bill, current_url))
      wrapper.add(list_widget_class_for_model(nested_model)(
          instance, current_url))

  context = qb2_nav_context(
      list_url(model_name), the_one_thing_on_this_page=wrapper)
  return render(request, 'qb2_base.html', context)
