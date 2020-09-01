""" This requires backbone.js and works together with crud_table.js to create
an html list that allows you to CRUD a filterable list of objects without any
page reloads. """
import json

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from djaveClassMagic.cases import (
    upper_case_singular, lower_case_singular, upper_case_plural,
    lower_case_plural)
from djaveClassMagic.edit_table import EditTable
from djaveHTML.field import Field, HiddenField
from djaveHTML.a import A


HIDDEN_NOT_DELETED_FILTER = HiddenField(
    'deleted', value='true', **{'data-query-key': 'deleted__isnull'})
HIDDEN_DELETED_FILTER = HiddenField(
    'deleted', value='false', **{'data-query-key': 'deleted__isnull'})


USE_DEFAULT = 'USE_DEFAULT'


class CRUDTable(object):
  def __init__(
      self, model, filter_widgets, display_columns, edit_field_names,
      save_new_defaults=None, label_edit_page_with_field=None, list_url=None,
      list_header=USE_DEFAULT, delete_row_confirm_question=USE_DEFAULT,
      hidden_filters=None, can_create_new=True, new_row_callback=None,
      saved_model_callback=None, deleted_model_callback=None,
      nav_css_class=None):
    self.model = model

    # A list of djaveHTML.field#Field
    self.filter_widgets = filter_widgets or []
    # A list of djaveHTML.field#HiddenField
    self.hidden_filters = hidden_filters or []
    for filter_widget in self.filter_widgets + self.hidden_filters:
      if not isinstance(filter_widget, Field):
        raise Exception(
            'Every filter widget and hidden filter must be a '
            'djaveHTML.field#Field')
      if not filter_widget.additional_attrs.get('data-query-key', None):
        raise Exception(
            'Every filter widget and hidden filter must specify a '
            'data-query-key e.g. create_date__lte or project__isnull')

    self.display_columns = display_columns  # A list of DisplayColumns
    self.edit_field_names = edit_field_names  # A list of strings
    # A dict, perhaps like {'user': 'me'}. These values get passed along to
    # /api/Project/2 or whatever when you save.
    self.save_new_defaults = save_new_defaults or {}
    # If you do 'name' and edit a Project (or whatever) whose name is
    # 'Exercise' then the edit panel will be titled "Edit Exercise" as opposed
    # to just "Edit project"
    self.label_edit_page_with_field = label_edit_page_with_field
    self.list_url = list_url or lower_case_plural(self.model)
    if list_header == USE_DEFAULT:
      list_header = upper_case_plural(self.model)
    self.list_header = list_header
    self.delete_row_confirm_question = ''
    if delete_row_confirm_question:
      if delete_row_confirm_question == USE_DEFAULT:
        self.delete_row_confirm_question = 'Delete this {}?'.format(
            lower_case_singular(model))
      else:
        self.delete_row_confirm_question = delete_row_confirm_question
    self.can_create_new = can_create_new
    self.new_row_callback = new_row_callback
    self.saved_model_callback = saved_model_callback
    self.deleted_model_callback = deleted_model_callback
    # When the list or edit panel is shown, explicitly say the css class of the
    # nav item that should get highlighted. In this way, you can have multiple
    # crud tables highlight the same navigation. For instance, the live and
    # archived project lists are both under the "Projects" nav.
    self.nav_css_class = nav_css_class

  def as_html(self):
    list_api_url = reverse(
        'list_or_save_new', kwargs={'model_name': self.model.__name__})
    # Otherwise this hands None to the template, which, being stupid, renders
    # 'None'
    label_edit_page_with_field = self.label_edit_page_with_field or ''

    context = {
        'list_api_url': list_api_url,
        'filter_widgets': self.filter_widgets,
        'hidden_filters': self.hidden_filters,
        'display_columns': self.display_columns,
        'edit_table': EditModelTable(self.model, self.edit_field_names),
        'upper_case_singular': upper_case_singular(self.model),
        'upper_case_plural': upper_case_plural(self.model),
        'lower_case_singular': lower_case_singular(self.model),
        'lower_case_plural': lower_case_plural(self.model),
        'list_url': self.list_url,
        'save_new_defaults': mark_safe(json.dumps(self.save_new_defaults)),
        'label_edit_page_with_field': label_edit_page_with_field,
        'list_header': self.list_header,
        'list_column_count': len(self.display_columns),
        'new_button': self.new_button(),
        'delete_row_confirm_question': self.delete_row_confirm_question,
        'new_row_callback': self.new_row_callback or 'null',
        'saved_model_callback': self.saved_model_callback or 'null',
        'deleted_model_callback': self.deleted_model_callback or 'null',
        'nav_css_class': self.nav_css_class or ''}
    return render_to_string('crud_table.html', context)

  def new_button(self):
    if self.can_create_new:
      new_button_text = 'New {}'.format(upper_case_singular(self.model))
      new_button_url = '{}/0'.format(self.list_url)
      new_button_css = 'new-{}'.format(lower_case_singular(self.model))
      return A(
          new_button_text, new_button_url, classes=[new_button_css],
          button=True)


class EditModelTable(EditTable):
  def __init__(self, model, edit_field_names):
    self.edit_field_names = edit_field_names
    super().__init__(model, None, None)

  def add_rows(self):
    self.add_field_rows(*self.edit_field_names)
