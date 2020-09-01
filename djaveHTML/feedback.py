from django.utils.safestring import mark_safe

from djaveHTML.element import Element


class Feedback(Element):
  def __init__(self, text, html_finder=None):
    self.text = text
    self.html_finder = html_finder

  def as_html(self):
    another_class = ''
    if self.html_finder:
      another_class = ' {}'.format(self.html_finder)
    return (
        '<span class="feedback{}">{}</span>'.format(another_class, self.text))


class DisappearingFeedback(Feedback):
  """ This is pretty much so I can briefly display "Saved!" on the page when
  the user clicks a Save button which causes a POST. """
  def __init__(self, text='Saved!', html_finder='hide_soon'):
    super().__init__(text, html_finder)

  def as_html(self):
    html = super().as_html()
    js = (
        '\n<script>'
        'setTimeout(function() {{ $(".{}").hide(); }}, 1000);'
        '</script>').format(self.html_finder)
    return mark_safe(html + js)
