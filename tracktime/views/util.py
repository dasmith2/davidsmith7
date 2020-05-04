from djaveNav.nav import NavItem, Nav


ENTER_TIME = 'enter_time'
ADD_UP_TIME = 'add_up_time'
TO_DO = 'to_do'
NAV_LIST = [
    NavItem(ENTER_TIME, 'Enter time'),
    NavItem(ADD_UP_TIME, 'Add up time'),
    NavItem(TO_DO, 'To do')]


def tt_ui_context(current_view, **kwargs):
  context = {'nav': Nav(NAV_LIST, current_view)}
  context.update(kwargs)
  return context
