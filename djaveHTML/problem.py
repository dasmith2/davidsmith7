from django.utils.safestring import mark_safe
from djaveHTML.element import Element


class Problem(Element):
  def __init__(self, text):
    self.text = text

  def as_html(self):
    return mark_safe('<span class="problem">{}</span>'.format(self.text))

  def as_csv(self):
    return ''
