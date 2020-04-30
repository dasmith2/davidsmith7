from djaveForm.button import Button
from djaveForm.field import Field


class Form(object):
  def __init__(self, form_elements=None):
    form_elements = form_elements or []
    self.form_elements = form_elements
    self._form_data_set = False

  def new_form_element(self, new_form_element):
    self.form_elements.append(new_form_element)
    return new_form_element

  def is_valid(self):
    valid_so_far = True
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        valid_so_far = valid_so_far and form_element.is_valid()
    return valid_so_far

  def explain_why_not_valid(self):
    to_return = []
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        explanation = form_element.explain_why_not_valid()
        if explanation:
          to_return.append(explanation)
    return ', '.join(to_return) or None

  def form_data_was_set(self):
    return self._form_data_set

  def set_form_data(self, values):
    self._form_data_set = True
    for form_element in self.form_elements:
      key_present = form_element.key() in values
      if isinstance(form_element, Button):
        form_element.set_was_clicked(key_present)
      elif key_present:
        if isinstance(form_element, Field):
          form_element.set_value(values[form_element.key()])
        else:
          raise Exception('I do not know how to set the value of a {}'.format(
              form_element.__class__))
