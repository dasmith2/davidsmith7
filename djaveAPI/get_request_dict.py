import json

from django.http import QueryDict


def get_request_dict(request):
  try:
    return json.loads(request.body)
  except json.decoder.JSONDecodeError:
    return QueryDict(request.body) or request.GET
