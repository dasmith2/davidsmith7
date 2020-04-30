views.py

from djAveJAX import ajax, AjaxProblem, get_ajax_variable

@ajax
def increment_foo(request):
  pk = get_ajax_variable(request.POST, 'pk', required=True)
  foo = Foo.objects.filter(pk=pk).first()
  if not foo:
    raise AjaxProblem('This Foo does not exist')
  foo.increment()
  return {'increment': 'successful'}

Javascript

function increment_foo(pk) {
  
}
