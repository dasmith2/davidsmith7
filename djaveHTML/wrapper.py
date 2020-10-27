from django.utils.safestring import mark_safe


class Wrapper(object):
  def __init__(self, *elements):
    self.elements = list(elements)

  def add(self, element):
    self.elements.append(element)

  def as_html(self):
    return mark_safe(
        '\n'.join([element.as_html() for element in self.elements]))
