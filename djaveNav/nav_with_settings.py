""" The difference between nav and nav_with_settings is nav_with_settings puts
account stuff to the right of the navigation. So you'll probably want to use
this for your top level navigation. """
from djaveNav.nav import Nav, NavItem


class NavWithAccount(Nav):
  def __init__(self, nav_list, settings_view_name, current_view_name):
    settings_nav_item = NavItem(settings_view_name, 'Settings')
    super().__init__(nav_list + [settings_nav_item], current_view_name)

  def template(self):
    return 'nav_with_settings.html'

  def context(self):
    return {
        'primary_nav_items': self.nav_items_current_or_not[:-1],
        'settings_nav': self.nav_items_current_or_not[-1]}
