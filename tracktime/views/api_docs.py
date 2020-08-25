from django.shortcuts import render
from djaveAPI.views.docs import api_doc_contents

from tracktime.views.nav_context import tracktime_context, SETTINGS


def api_docs(request):
  model_names = [
      'Project', 'ProjectWorkSession', 'ProjectToDo', 'ProjectInvoiceRule',
      'ProjectInvoice', 'ProjectLineItem', 'ManualLineItem']
  model_docs = api_doc_contents(request, model_names)
  context = tracktime_context(
      request.user, SETTINGS, model_docs=model_docs, title='API')
  return render(request, 'api_docs_tracktime.html', context)
