from django.utils.safestring import mark_safe

from djaveHTML.element import StringElement


class Paragraph(StringElement):
  def as_html(self):
    return mark_safe('<p>{}</p>'.format(super().as_html()))
