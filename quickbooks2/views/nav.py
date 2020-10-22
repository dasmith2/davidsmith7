from djaveNav.nav import NavItem
from djaveNav.nav import Nav


def qb2_nav_context(current_view, **kwargs):
  context = {'nav': qb2_nav(current_view)}
  context.update(kwargs)
  return context


def qb2_nav(current_view):
  return Nav(
      [NavItem('qb2_customers', 'Customers', True)],
      current_view)
