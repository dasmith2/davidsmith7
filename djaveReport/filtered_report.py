from django.template import loader
from djaveForm.button import Button
from djaveForm.form import Form
from djaveForm.form_element import FormElement


class FilteredReport(object):
  def __init__(self, request_get=None, filters=None, contents=None):
    """ request_get is a dictionary like object, almost certainly request.GET
    filters is a list of djaveForm.form_element.FormElement
    contents is a single, or list of objects with an as_html function """
    self.set_filters(filters, request_get)
    self.set_contents(contents)
    self.report_button = Button('Report')

  def as_html(self):
    template = loader.get_template('filtered_report.html')
    context = {
        'filters': self._filters, 'contents': self._contents,
        'report_button': self.report_button}
    return template.render(context)

  def set_filters(self, filters, request_get):
    self._filters = self._validate_filters(filters)
    self.request_get = request_get
    if request_get:
      Form(self._filters).set_form_data(request_get)

  def get_query_string(self):
    return Form(self._filters).to_query_string()

  def get_query_dict(self):
    return Form(self._filters).to_query_dict()

  def _validate_filters(self, filters):
    if filters is None:
      return []
    if not isinstance(filters, list):
      raise Exception('filters should be a list')
    for _filter in filters:
      if not isinstance(_filter, FormElement):
        raise Exception((
            'Every filter should be a djaveForm.form_element.FormElement but '
            'this filter is a {}').format(_filter.__class__))
    return filters

  def set_contents(self, contents):
    self._contents = self._validate_contents(contents)

  def add_content(self, content):
    self._validate_content(content)
    self._contents.append(content)

  def _validate_contents(self, contents):
    if contents is None:
      return []
    if isinstance(contents, list):
      for _content in contents:
        self._validate_content(_content)
      return contents
    self._validate_content(contents)
    return [contents]

  def _validate_content(self, _content):
    if not hasattr(_content, 'as_html'):
      raise Exception(
          'Content of type {} needs an as_html function'.format(
              _content.__class__))
