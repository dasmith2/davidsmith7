from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from djavError.views.util import error_context, ERRORS
from djavError.widgets.errors_report import ErrorsReport


@user_passes_test(lambda u: u.is_superuser)
def errors(request):
  context = error_context(
      ERRORS, the_one_thing_on_the_page=ErrorsReport(request.GET))
  return render(request, 'error_base.html', context)
