from django.shortcuts import render, reverse


def homepage(request):
  context = {
      'logged_in': request.user.is_authenticated,
      'enter_time_url': reverse('enter_time'),
      'login_url': reverse('djave_login'),
      'sign_up_url': reverse('djave_sign_up'),
      'api_docs_url': reverse('tracktime_api_docs')}
  return render(request, 'tracktime_homepage.html', context)
