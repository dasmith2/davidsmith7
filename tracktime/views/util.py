from djaveNav.nav import NavItem
from djaveNav.nav_with_settings import NavWithAccount


ENTER_TIME = 'enter_time'
TO_DO = 'to_do'
REPORT = 'report'
PROJECTS = 'projects'
SETTINGS = 'settings_tracktime'
NAV_LIST = [
    NavItem(ENTER_TIME, 'Enter time'),
    NavItem(TO_DO, 'To do'),
    NavItem(REPORT, 'Report'),
    NavItem(PROJECTS, 'Projects')]


def tracktime_context(current_view, request, **kwargs):
  context = {'nav': NavWithAccount(
      NAV_LIST, SETTINGS, current_view, request)}
  context.update(kwargs)
  return context
