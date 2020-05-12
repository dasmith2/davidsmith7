from collections import namedtuple
from datetime import timedelta

from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist
from django.shortcuts import reverse
from djaveDT import days_ago_str, now
from djaveNav import url_with_date, date_to_url_str


RollerDay = namedtuple('RollerDay', 'is_current text css_class url date_str')


class DateRoller(object):
  """
  In your views,

  from djaveNav.date_roller import DateRoller
  from djaveNav import date_from_url

  def my_view(request):
    day = date_from_url(request)
    return render(request, 'my_view.html', {
        'date_roller': DateRoller('my_view', day)})

  In my_view.html,

  {{ date_roller.as_html|safe }}
  """
  def __init__(self, view_name, on_day, max_day=None, min_day=None):
    self.view_name = view_name
    self.on_day = on_day
    self.max_day = max_day
    self.min_day = min_day

  def as_html(self, nnow=None):
    nnow = nnow or now()
    today = nnow.date()
    days = []
    day_delta_and_css_classes = [
        (-2, 'two_before'),
        (-1, 'one_before'),
        (0, ''),
        (1, 'one_after'),
        (2, 'two_after')]
    for day_delta, css_class in day_delta_and_css_classes:
      this_day = self.on_day + timedelta(days=day_delta)
      if self.min_day and this_day < self.min_day:
        continue
      if self.max_day and this_day > self.max_day:
        continue
      is_current = this_day == self.on_day
      text = days_ago_str(this_day)
      if this_day == today:
        url = reverse('enter_time')
      else:
        url = url_with_date(reverse('enter_time'), day=this_day)
      days.append(RollerDay(
          is_current, text, css_class, url, date_to_url_str(this_day)))
    try:
      return render_to_string('date_roller.html', {'days': days})
    except TemplateDoesNotExist:
      raise Exception(
          'In order to use the date roller you need to add djaveNav/templates '
          'to the DIRS attribute in the TEMPLATES setting')
