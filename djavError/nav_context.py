from djaveNav.nav import ViewNavItem, Nav
from djavError.models.error import Error
from djavError.models.notification import Notification
from djavError.models.long_request import LongRequest
from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.models.fixable import get_last_week_unfixed_count


ERRORS = ViewNavItem('errors', 'Errors', True)
NOTIFICATIONS = ViewNavItem('notifications', 'Notifications', True)
LONG_REQUESTS = ViewNavItem('long_requests', 'Long requests', True)
TOO_MANY_QUERIES = ViewNavItem('too_many_queries', 'Too many queries', True)
TRIGGER_ERRORS = ViewNavItem('trigger_errors', 'Trigger', True)

NAV_LIST = [
    ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES, TRIGGER_ERRORS]


def nav_context(current_view, **kwargs):
  use_nav_list = []
  for nav in NAV_LIST:
    how_many = get_how_many(nav.view_name)
    display = '{} ({})'.format(nav.display, how_many)
    if how_many is None:
      display = nav.display
    use_nav_list.append(ViewNavItem(nav.view_name, display, True))
  context = {'nav': Nav(use_nav_list, current_view)}
  context.update(kwargs)
  return context


def get_how_many(view_name):
  if view_name == 'trigger_errors':
    return None
  elif view_name == 'errors':
    return get_last_week_unfixed_count(Error)
  elif view_name == 'notifications':
    return get_last_week_unfixed_count(Notification)
  elif view_name == 'long_requests':
    return get_last_week_unfixed_count(LongRequest)
  elif view_name == 'too_many_queries':
    return get_last_week_unfixed_count(TooManyQueriesRequest)
  raise Exception(view_name)
