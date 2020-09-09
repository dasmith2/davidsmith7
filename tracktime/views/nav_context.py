from django.utils.safestring import mark_safe
from djaveNav.nav import NavItem
from djaveNav.nav import Nav
from djaveNav.nav_with_settings import NavWithAccount

from tracktime.models.project import Project


ENTER_TIME = 'enter_time'
TO_DO = 'to_dos'
PROJECT_WORK_SESSION_SUMMARY = 'project_work_summary'
PROJECTS = 'projects'
INVOICES = 'project_invoices'
SETTINGS = 'settings_tracktime'


def tracktime_context(user, current_view, **kwargs):
  context = {'nav': tracktime_nav(user, current_view)}
  context.update(kwargs)
  return context


def tracktime_nav(user, current_view):
  use_clock = False
  has_to_do_list = False
  has_invoices = False
  if user.is_authenticated:
    for project in Project.allowed_by_user_live(user):
      use_clock = use_clock or project.use_clock
      has_to_do_list = has_to_do_list or project.has_to_do_list
      has_invoices = has_invoices or project.has_invoices
    nav_list = []
    nav_list.append(NavItem(ENTER_TIME, 'Clock', use_clock))
    nav_list.append(NavItem(TO_DO, 'To do', has_to_do_list))
    nav_list.append(NavItem(PROJECT_WORK_SESSION_SUMMARY, 'Report', use_clock))
    nav_list.append(NavItem(INVOICES, 'Invoices', has_invoices))
    nav_list.append(NavItem(PROJECTS, 'Projects', True))
    return NavWithAccount(nav_list, SETTINGS, current_view)
  else:
    return Nav(
        [NavItem('tracktime_homepage', mark_safe('&laquo; Home'))],
        'tracktime_homepage')
