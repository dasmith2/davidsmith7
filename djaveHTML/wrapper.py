from django.utils.safestring import mark_safe


class Wrapper(object):
  def __init__(self, *elements):
    self.elements = elements

  def as_html(self):
    return mark_safe(
        '\n'.join([element.as_html() for element in self.elements]))
