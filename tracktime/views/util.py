from djaveNav.nav import NavItem
from djaveNav.nav_with_settings import NavWithAccount


ENTER_TIME = 'enter_time'
TO_DO = 'to_do'
PROJECT_WORK_SESSION_SUMMARY = 'project_work_summary'
PROJECTS = 'projects'
INVOICES = 'project_invoices'
SETTINGS = 'settings_tracktime'
NAV_LIST = [
    NavItem(ENTER_TIME, 'Enter time'),
    NavItem(TO_DO, 'To do'),
    NavItem(PROJECT_WORK_SESSION_SUMMARY, 'Report'),
    NavItem(INVOICES, 'Invoices'),
    NavItem(PROJECTS, 'Projects')]


def tracktime_context(current_view, **kwargs):
  context = {'nav': NavWithAccount(NAV_LIST, SETTINGS, current_view)}
  context.update(kwargs)
  return context
