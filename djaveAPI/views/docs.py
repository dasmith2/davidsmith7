from djaveAPI.model_api_docs import model_api_docs
from djaveURL import protocol_and_host


def api_doc_contents(request, model_names):
  api_root_url = protocol_and_host(request)
  model_docs = []
  for model_name in model_names:
    model_docs.append(model_api_docs(model_name, api_root_url))
  return model_docs
