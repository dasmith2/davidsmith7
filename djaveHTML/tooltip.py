from django.utils.safestring import mark_safe

from djaveHTML.element import Element


class Tooltip(Element):
  def __init__(self, label, help_text, width=None):
    self.label = label
    self.help_text = help_text
    self.width = width

  def as_html(self):
    width_str = ''
    if self.width:
      width_str = ' style="width: {}px;"'.format(self.width)
    template = (
        '<div class="tooltip">{}<span class="tooltiptext"{}>{}</span></div>')
    return mark_safe(template.format(self.label, width_str, self.help_text))

  def as_csv(self):
    return self.label
