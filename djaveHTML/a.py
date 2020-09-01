from django.utils.safestring import mark_safe

from djaveHTML.element import Element, elements_as_html, elements_as_csv
from djaveHTML.slugify import slugify


class A(Element):
  def __init__(self, elements, url, classes=None, button=False):
    self.elements = elements
    self.url = url
    self.classes = classes or []
    if button:
      self.classes.append('button')

  def as_html(self):
    classes_str = ''
    if self.classes:
      classes_str = ' class="{}"'.format(' '.join(self.classes))
    return mark_safe('<a href="{}"{}>{}</a>'.format(
        self.url, classes_str, elements_as_html(self.elements)))

  def as_csv(self):
    return elements_as_csv(self.elements)


class AButton(A):
  def __init__(self, elements, url, classes=None):
    classes = classes or []
    classes.append('button')
    if isinstance(elements, str):
      classes.append(slugify(elements))
    super().__init__(elements, url, classes=classes)
