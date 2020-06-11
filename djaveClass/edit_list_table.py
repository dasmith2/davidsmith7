""" This table is for editing a list of objects. It does one row per object.
"""

from djaveTable.table import Table


class EditListTable(Table):
  def __init__(self, model, *args, **kwargs):
    self.model = model

    if 'additional_attrs' not in kwargs or kwargs['additional_attrs'] is None:
      kwargs['additional_attrs'] = {}
    kwargs['additional_attrs']['data-model'] = model.__name__

    super().__init__(*args, **kwargs)

  def wire_up_edit_ajax(self, columns):
    entries = []
    for column in columns:
      entries.append(
          "wire_up_ajax_save_field('.{}', '{}');".format(column, column))
    self._append_js('\n'.join(entries))

  def wire_up_delete_ajax(self, selector, confirm_question):
    confirm_question = confirm_question.replace(
        "'", r"\'").replace('\n', r'\n')
    new_js = "wire_up_ajax_delete_button('{}', '{}');".format(
        selector, confirm_question)
    self._append_js(new_js)

  def _append_js(self, new_js):
    if not self.js:
      self.js = ''
    self.js = '{}\n{}'.format(self.js, new_js)
