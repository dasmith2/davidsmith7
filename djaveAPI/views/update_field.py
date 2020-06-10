from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import (
    get_request_variable, get_obj_from_request_pk)
from djaveAPI.problem import Problem
from djaveClass.find_models import model_from_name
from djaveClass.model_fields import model_fields
from djavError.models import log_error


@ajax_endpoint_login_required
def update_field(request):
  """ model_name should be the name of a Publishable model. This function will
  update a single field on a publishable object which is very handy for
  creating html tables full of editable fields. """
  model_name = get_request_variable(request.POST, 'model_name')
  field_name = get_request_variable(request.POST, 'field_name')
  new_value = get_request_variable(request.POST, 'new_value', required=False)
  print('{}.{} = {}'.format(model_name, field_name, new_value)) # DO NOT SUBMIT

  model = model_from_name(model_name)
  if not model:
    raise Problem('I was unable to find a model named {}'.format(model_name))
  instance = get_obj_from_request_pk(request, model)
  if hasattr(instance, 'as_child_class'):
    instance = instance.as_child_class()

  if not instance.user_allowed(request.user):
    message = (
        'User {} is trying to modify {} {}\nThe more likely scenario is a '
        'programming issue with {}.user_allowed.').format(
            request.user.pk, model.__name__, instance.pk, model.__name__)
    log_error('Is this user really hacking update_field?', message)
    raise Problem('You do not have permission to edit this line item')

  if not hasattr(instance, field_name):
    raise Problem('{} does not have a {} field'.format(model_name, field_name))
  if model_fields(model, specific_field=field_name).required and not new_value:
    raise Problem('Required')

  setattr(instance, field_name, new_value)

  why_invalid = instance.explain_why_invalid()
  if why_invalid:
    raise Problem(why_invalid)

  # I don't simply instance.save() here because of a race. If you can edit 2
  # fields in a row, you edit them both. When you hit save, 2 requests fire
  # simultaneously.
  model.all.filter(pk=instance.pk).update(**{field_name: new_value})
