from django.shortcuts import render, get_object_or_404
from djaveClassMagic.instance_to_html import instance_to_html
from djaveLogin.login_required import login_required

from quickbooks2.models.customer import Customer
from quickbooks2.views.nav import qb2_nav_context
from quickbooks2.widgets.customers import Customers


@login_required
def qb2_customers(request):
  context = qb2_nav_context(
      'qb2_customers', the_one_thing_on_this_page=Customers())
  return render(request, 'qb2_base.html', context)


@login_required
def qb2_customer(request, pk):
  customer = get_object_or_404(Customer.allowed_by_user(request.user), pk=pk)

  context = qb2_nav_context(
      'qb2_customers',
      the_one_thing_on_this_page=instance_to_html(customer))
  return render(request, 'qb2_base.html', context)
