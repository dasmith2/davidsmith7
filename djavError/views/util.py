from djaveNav.nav import NavItem, Nav
from djavError.widgets.errors_report import get_errors
from djavError.widgets.notifications_report import get_notifications

ERRORS = NavItem('errors', 'Errors')
NOTIFICATIONS = NavItem('notifications', 'Notifications')
LONG_REQUESTS = NavItem('long_requests', 'Long requests')
TOO_MANY_QUERIES = NavItem('too_many_queries', 'Too many queries')

NAV_LIST = [ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES]


def error_context(current_view, **kwargs):
  use_nav_list = []
  for nav in NAV_LIST:
    how_many = get_how_many(nav.view_name)
    use_nav_list.append(NavItem(
        nav.view_name, '{} ({})'.format(nav.display, how_many)))
  context = {'nav': Nav(use_nav_list, current_view)}
  context.update(kwargs)
  return context


def get_how_many(view_name):
  if view_name == 'errors':
    return get_errors().count()
  elif view_name == 'notifications':
    return get_notifications().count()
  return 0
