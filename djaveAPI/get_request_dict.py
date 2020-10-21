import json

from django.http import QueryDict


def get_request_dict(request):
  if isinstance(request, dict):
    return request
  if isinstance(request, QueryDict):
    return request.dict()
  try:
    return json.loads(request.body)
  except json.decoder.JSONDecodeError:
    # bool(QueryDict('')) is False
    return (QueryDict(request.body) or request.GET).dict()
