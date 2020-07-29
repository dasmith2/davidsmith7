from collections import namedtuple
import re

from django.shortcuts import reverse
from django.template.loader import render_to_string


NavItem = namedtuple('NavItem', 'view_name display')
NavItemCurrentOrNot = namedtuple(
    'NavItemCurrentOrNot', 'url display is_current css_class')


class Nav(object):
  def __init__(self, nav_list, current_view_name_or_nav_item=None):
    self.nav_list = nav_list
    current_view_name = current_view_name_or_nav_item
    if current_view_name and isinstance(
        current_view_name_or_nav_item, NavItem):
      current_view_name = current_view_name_or_nav_item.view_name
    found_current = False
    self.nav_items_current_or_not = []
    self._title = None
    for nav_item in nav_list:
      if not isinstance(nav_item, NavItem):
        raise Exception('nav_list should be a list of NavItem objects')
      is_current = nav_item.view_name == current_view_name or (
          nav_item.display == current_view_name)
      if is_current:
        self._title = nav_item.display
      found_current = found_current or is_current
      css_class = '{}_nav nav_item'.format(
          re.compile(r'[^\w]').sub('', nav_item.display.lower()))
      self.nav_items_current_or_not.append(
          NavItemCurrentOrNot(
              reverse(nav_item.view_name), nav_item.display, is_current,
              css_class))
    # Don't raise an exception here if current_view_name and not found_current.
    # Nav entries disappear now depending on what features you have enabled. So
    # if, for instance, you have one project with a clock so "Enter time" is
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
      return self.nav_items_current_or_not[0]
