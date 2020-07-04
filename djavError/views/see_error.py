from django.http import HttpResponse
from djavError.models.error import Error


def see_error(request, pk):
  error = Error.objects.get(pk=pk)
  parts = [
      error.title,
      error.message,
      error.error_message,
      error.stack_trace]
  return HttpResponse(
      '\n'.join(['<pre>{}</pre>'.format(part) for part in parts]))
