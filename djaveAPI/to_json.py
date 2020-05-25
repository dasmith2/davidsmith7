""" Turn an object into JSON suitable for publishing in an API. """
from djaveAPI.discover_schema import api_fields, DATE_TIME, DATE


def to_json_dict(obj):
  model = obj._meta.model
  as_dict = {'type': model.__name__}
  for field in api_fields(model):
    value = None
    if field.foreign_key_to:
      value = getattr(obj, '{}_id'.format(field.name))
    else:
      value = getattr(obj, field.name)
      if value is not None:
        if field.type in [DATE_TIME, DATE]:
          value = value.isoformat()
    as_dict[field.name] = value
  return as_dict


def example_to_json():
  from tracktime.models.project_work_session import ProjectWorkSession
  return to_json_dict(ProjectWorkSession.live.first())
