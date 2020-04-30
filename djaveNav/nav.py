from collections import namedtuple

from django.shortcuts import reverse
from django.template.loader import render_to_string


NavItem = namedtuple('NavItem', 'view_name display')
NavItemCurrentOrNot = namedtuple(
    'NavItemCurrentOrNot', 'url display is_current')


class Nav(object):
  def __init__(self, nav_list, current_view_name):
    found_current = False
    self.nav_items_current_or_not = []
    for nav_item in nav_list:
      if not isinstance(nav_item, NavItem):
        raise Exception('nav_list should be a list of NavItem objects')
      is_current = nav_item.view_name == current_view_name or (
          nav_item.display == current_view_name)
      found_current = found_current or is_current
      self.nav_items_current_or_not.append(
          NavItemCurrentOrNot(
              reverse(nav_item.view_name), nav_item.display, is_current))
    if not found_current:
      raise Exception(
          'I was unable to find {} in the nav_list'.format(current_view_name))

  def as_html(self):
    return render_to_string('nav.html', {
        'nav_items_current_or_not': self.nav_items_current_or_not})
