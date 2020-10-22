from django.shortcuts import reverse
from djaveClassMagic.cases import upper_case_plural
from djaveClassMagic.find_models import all_models
from djaveNav.nav import URLNavItem
from djaveNav.nav import Nav

from quickbooks2.models.quickbooks_object import QuickBooksObject


def qb2_nav_context(current_url, **kwargs):
  context = {'nav': qb2_nav(current_url)}
  context.update(kwargs)
  return context


def qb2_nav(current_url):
  nav_items = []
  for model in all_models(subclass_of=QuickBooksObject):
    list_url = reverse(
        'quickbooks2_model_list',
        kwargs={'model_name': model._meta.model_name})
    nav_items.append(URLNavItem(list_url, upper_case_plural(model), True))
  return Nav(nav_items, current_url)
