from django.shortcuts import render
from djaveLogin.login_required import login_required

from quickbooks2.views.nav import qb2_nav_context
from quickbooks2.widgets.customers import Customers


@login_required
def qb2_customers(request):
  context = qb2_nav_context(
      'qb2_customers', the_one_thing_on_this_page=Customers())
  return render(request, 'qb2_base.html', context)
