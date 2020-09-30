from django.core.exceptions import FieldError, ValidationError
from djaveAPI.find_models import allowed_model_from_name
from djaveAPI.get_request_dict import get_request_dict
from djaveAPI.problem import Problem


def filter_model(model_or_model_name, credentials, request_GET):
  model = allowed_model_from_name(model_or_model_name)

  queryset = credentials.allowed_list(model)

  for key, value in get_request_dict(request_GET).items():
    if value.lower() in ['true', 'false']:
      value = value.lower() == 'true'
    try:
      queryset = queryset.filter(**{key: value})
    except FieldError:
      pass  # For instance, ?page=1 causes this.
    except TypeError as ex:
      raise Problem(ex.args[0])
    except ValidationError as ex:
      raise Problem(str(ex))
  return queryset
