import json

from djaveAPI.problem import Problem


def get_posted_json(request):
  try:
    return json.loads(request.body)
  except json.decoder.JSONDecodeError:
    raise Problem('The request contained invalid JSON')
