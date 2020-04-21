from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/admin/login/')
def time_entry(request):
  return render(request, 'time_entry.html', {})
