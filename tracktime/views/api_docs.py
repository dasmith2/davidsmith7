from djaveAPI.views import generic_api_docs
from djaveURL import protocol_and_host


def api_docs(request):
  model_names = ['Project', 'ProjectWorkSession', 'ToDo']
  return generic_api_docs(request, model_names, protocol_and_host(request))
