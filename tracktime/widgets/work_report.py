from django.template import loader
from djaveReport.date_range_report import FROM_DATE, TO_DATE
from djaveURL import date_to_url_str

from tracktime.models.work_session_description import WorkSessionDescriptions


def work_report_url_dict(from_date=None, to_date=None):
  query_dict = {}
  if from_date:
    query_dict[FROM_DATE] = date_to_url_str(from_date)
  if to_date:
    query_dict[TO_DATE] = date_to_url_str(to_date)
  return query_dict


class WorkReportContent(object):
  def __init__(self, user, from_date, to_date, tz_str=None):
    self.user = user
    self.from_date = from_date
    self.to_date = to_date
    self.tz_str = tz_str

    self.work_session_descriptions = (
        self.get_work_session_descriptions_object())

  def get_work_session_descriptions_object(self):
    return WorkSessionDescriptions(
        user=self.user,
        from_date=self.from_date,
        to_date=self.to_date,
        tz_str=self.tz_str)

  def get_descriptions(self):
    return self.work_session_descriptions.get_work_session_descriptions()

  def get_total(self):
    return round(self.work_session_descriptions.get_total(), 2)

  def as_html(self):
    template = loader.get_template('work_report.html')
    context = {
        'work_session_descriptions': self.get_descriptions(),
        'header': self.html_header()}
    return template.render(context)

  def html_header(self):
    return 'Total: {} hours'.format(self.get_total())
