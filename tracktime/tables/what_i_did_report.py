from datetime import timedelta

from django.shortcuts import reverse
from django.template import loader
from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from djaveURL import dict_as_query

from tracktime.models.to_do import ToDo
from tracktime.models.tracked import Tracked


class WhatIDidReport(DateRangeReport):
  def __init__(self, request_get, user, nnow=None):
    nnow = nnow or now()
    default_from_date = nnow.date() - timedelta(days=7)
    default_to_date = nnow.date()
    super().__init__(default_from_date, default_to_date, request_get)

    current_query_dict = self.get_query_dict()
    content = WhatIDidReportContent(
        user, self.from_date(), self.to_date(), current_query_dict)
    self.add_content(content)


class WhatIDidReportContent(object):
  def __init__(self, user, from_date, to_date, current_query_dict):
    self.projects = {}
    for tracked in Tracked.live.by_user_and_date_range(
        user, from_date, to_date):
      if tracked.hours:
        if tracked.project not in self.projects:
          self.projects[tracked.project] = WhatIDidPerProject(
              tracked.project, current_query_dict)
        self.projects[tracked.project].hours = round(
            self.projects[tracked.project].hours + tracked.hours, 2)
    for to_do in ToDo.live.done_by_user_in_date_range(
        user, from_date, to_date).order_by('-pk'):
      if to_do.project not in self.projects:
        self.projects[to_do.project] = WhatIDidPerProject(
            to_do.project, current_query_dict)
      self.projects[to_do.project].to_dos.append(to_do)

  def as_html(self):
    template = loader.get_template('what_i_did.html')
    context = {'projects': list(self.projects.values())}
    return template.render(context)


class WhatIDidPerProject(object):
  def __init__(self, project, current_query_dict):
    self.name = project.name
    self.to_dos = []
    self.hours = 0.0
    # This is why the WhatIDidPerProject filters should be exactly the same as
    # the TimeBreakdown filters, except time breakdown is also by project.
    use_query_dict = {'project': project.pk}
    use_query_dict.update(current_query_dict)
    self.hours_breakdown_url = reverse(
        'time_breakdown') + dict_as_query(use_query_dict)
