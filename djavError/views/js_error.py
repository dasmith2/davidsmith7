from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from djavError.log_error import log_error


@csrf_exempt
def js_error(request):
  post = request.POST
  message = (
      'This is a Javascript error caught by '
      'main/templates/js/error.js\n\nuser: {}\n\n{} line {} column {}'
      '\nReferer {}\nStack {}').format(
          request.user, post.get('url', ''),
          post.get('line', ''), post.get('col', ''),
          request.META.get('HTTP_REFERER', ''), post.get('stack', ''))
  subject = post.get('msg', 'Javascript error received')
  log_error(subject, message, supress_stack_trace=True)
  return HttpResponse('ok')
