from django.shortcuts import render
from djaveAPI.views.docs import api_doc_contents

from tracktime.views.util import tracktime_context, SETTINGS


def api_docs(request):
  model_names = [
      'User', 'Project', 'ProjectWorkSession', 'ProjectToDo', 'ProjectInvoice',
      'ProjectLineItem', 'ManualLineItem']
  model_docs = api_doc_contents(request, model_names)
  context = tracktime_context(SETTINGS, request, model_docs=model_docs)
  return render(request, 'api_docs_tracktime.html', context)
