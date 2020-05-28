from django.shortcuts import render
from djaveAPI.views import api_doc_contents

from tracktime.views.util import tracktime_context, SETTINGS


def api_docs(request):
  model_names = ['Project', 'ProjectWorkSession', 'ToDo']
  model_docs = api_doc_contents(request, model_names)
  context = tracktime_context(SETTINGS, request, model_docs=model_docs)
  return render(request, 'api_docs_tracktime.html', context)
