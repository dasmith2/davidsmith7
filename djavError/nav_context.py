from djaveNav.nav import NavItem, Nav
from djavError.models.error import Error
from djavError.models.notification import Notification
from djavError.models.long_request import LongRequest
from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.widgets.fixable_report import get_fixables


ERRORS = NavItem('errors', 'Errors')
NOTIFICATIONS = NavItem('notifications', 'Notifications')
LONG_REQUESTS = NavItem('long_requests', 'Long requests')
TOO_MANY_QUERIES = NavItem('too_many_queries', 'Too many queries')
TRIGGER_ERRORS = NavItem('trigger_errors', 'Trigger')

NAV_LIST = [
    ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES, TRIGGER_ERRORS]


def nav_context(current_view, **kwargs):
  use_nav_list = []
  for nav in NAV_LIST:
    how_many = get_how_many(nav.view_name)
    display = '{} ({})'.format(nav.display, how_many)
    if how_many is None:
      display = nav.display
    use_nav_list.append(NavItem(nav.view_name, display))
  context = {'nav': Nav(use_nav_list, current_view)}
  context.update(kwargs)
  return context


def get_how_many(view_name):
  if view_name == 'trigger_errors':
    return None
  elif view_name == 'errors':
    return get_fixables(Error).count()
  elif view_name == 'notifications':
    return get_fixables(Notification).count()
  elif view_name == 'long_requests':
    return get_fixables(LongRequest).count()
  elif view_name == 'too_many_queries':
    return get_fixables(TooManyQueriesRequest).count()
  return 0
