from django.utils.safestring import mark_safe

from djaveHTML.element import Element, elements_as_html, elements_as_csv
from djaveHTML.slugify import slugify


class A(Element):
  def __init__(self, elements, url, css_classes=None):
    super().__init__(css_classes=css_classes)
    self.elements = elements
    self.url = url

  def as_html(self):
    return mark_safe('<a href="{}"{}>{}</a>'.format(
        self.url, self.css_class_str(), elements_as_html(self.elements)))

  def as_csv(self):
    return elements_as_csv(self.elements)


class AButton(A):
  def __init__(self, elements, url, css_classes=None):
    super().__init__(elements, url, css_classes=css_classes)
    self.add_css_class('button')
    if isinstance(elements, str):
      self.add_css_class(slugify(elements))
