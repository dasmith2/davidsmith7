from djaveNav.nav import NavItem, Nav


ENTER_TIME = 'enter_time'
TO_DO = 'to_do'
REPORT = 'report'
PROJECTS = 'projects'
NAV_LIST = [
    NavItem(ENTER_TIME, 'Enter time'),
    NavItem(TO_DO, 'To do'),
    NavItem(REPORT, 'Report'),
    NavItem(PROJECTS, 'Projects')]


def tracktime_context(current_view, **kwargs):
  context = {'nav': Nav(NAV_LIST, current_view)}
  context.update(kwargs)
  return context
