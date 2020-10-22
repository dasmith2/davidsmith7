"""
For instance,

def projects(request):
  return render(request, 'whatever.html', {
      'nav': Nav([
          ViewNavItem('projects', 'Projects', True),
          ViewNavItem('project_to_dos', 'To do', True)], 'projects'))

{{ nav.as_html }}

"""
from collections import namedtuple
import re

from django.shortcuts import reverse
from django.template.loader import render_to_string


# You can use ViewNavItem when every nav item has its own view.
class ViewNavItem(namedtuple('ViewNavItem', 'view_name display is_visible')):
  def get_url(self):
    return reverse(self.view_name)


# When a url encodes, say, model name and shows something completely different,
# but it's technically the same view, you'll have to use a URLNavItem which is
# based on url instead of view name.
class URLNavItem(namedtuple('URLNavItem', 'url display is_visible')):
  def get_url(self):
    return self.url


NavItemCurrentOrNot = namedtuple(
    'NavItemCurrentOrNot', 'url display is_current css_class is_visible')


def _nav_item_identifier(nav_item):
  if isinstance(nav_item, str):
    return nav_item
  elif isinstance(nav_item, ViewNavItem):
    return nav_item.view_name
  elif isinstance(nav_item, URLNavItem):
    return nav_item.url
  raise Exception(nav_item)


def _abstract_nav_item(nav_item):
  return namedtuple('AbstractNavItem', 'identifier display is_visible')(
      _nav_item_identifier(nav_item), nav_item.display, nav_item.is_visible)


class Nav(object):
  def __init__(self, nav_list, current=None):
    """ current can be a view_name if you're using ViewNavItems, it can be a
    url if you're using URLNavItem, or it can just be a *NavItem out of
    nav_list. """
    self.nav_list = nav_list

    current = _nav_item_identifier(current)

    found_current = False
    self.nav_items_current_or_not = []
    self._title = None
    for nav_item in nav_list:
      next_identifier = _nav_item_identifier(nav_item)

      is_current = current in (next_identifier, nav_item.display)

      if is_current:
        self._title = nav_item.display
      found_current = found_current or is_current
      css_class = '{}_nav nav_item'.format(
          re.compile(r'[^\w]').sub('', next_identifier.lower()))
      self.nav_items_current_or_not.append(
          NavItemCurrentOrNot(
              nav_item.get_url(), nav_item.display, is_current,
              css_class, nav_item.is_visible))
    # Don't raise an exception here if current and not found_current. Nav
    # entries disappear now depending on what features you have enabled. So if,
    # for instance, you have one project with a clock so "Enter time" is
    # visible, but you're on the projects page and you archive your only
    # project, and THEN click on "Enter time", you land on a page without a nav
    # that's smart enough to tell you to go make a project. So that works fine.

  def title(self):
    return self._title

  def template(self):
    return 'nav.html'

  def context(self):
    return {'primary_nav_items': self.nav_items_current_or_not}

  def as_html(self):
    return render_to_string(self.template(), self.context())

  def first_nav_item_current_or_not(self):
    if self.nav_items_current_or_not:
      for nav_item in self.nav_items_current_or_not:
        if nav_item.is_visible:
          return nav_item
