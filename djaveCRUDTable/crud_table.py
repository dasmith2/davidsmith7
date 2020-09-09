""" This requires backbone.js and works together with crud_table.js to create
an html list that allows you to CRUD a filterable list of objects without any
page reloads.

If your table stays invisible, a likely culprit is that the browser's url
doesn't match the list_url. It's programmed to show the list and the edit panel
only when they match the browser's url. """
from datetime import date, timedelta
import json

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from djaveClassMagic.cases import (
    upper_case_singular, lower_case_singular, upper_case_plural,
    lower_case_plural)
from djaveClassMagic.edit_table import EditTable
from djaveHTML.field import Field, HiddenField, DateField
from djaveHTML.a import A


def hidden_filter(field_name, value, data_query_key=None):
  return HiddenField(
      field_name, value=value,
      **{'data-query-key': data_query_key or field_name})


HIDDEN_NOT_DELETED_FILTER = hidden_filter('deleted', 'true', 'deleted__isnull')
HIDDEN_DELETED_FILTER = hidden_filter('deleted', 'false', 'deleted__isnull')
USE_DEFAULT = 'USE_DEFAULT'


def from_filter(field_name, default=None):
   default = default or date.today() - timedelta(days=7)
   field = DateField(
       'from_date', default=default, label='From',
       query_key='{}__gte'.format(field_name))
   field.do_beginning_of_day()
   return field


def to_filter(field_name, default=None):
  default = default or date.today()
  field = DateField(
      'to_date', default=default, label='To',
      query_key='{}__lte'.format(field_name))
  field.do_end_of_day()
  return field


class CRUDTable(object):
  # djaveCRUDTable/(crud_table.py (def __init__ args and body, as_html),
  # templates/(crud_table.html bottom of the page, js/crud_table.js
  # crud_table_options))
  def __init__(
      self, model, display_columns, filter_widgets=None, edit_field_names=None,
      save_new_defaults=None, label_edit_page_with_field=None, list_url=None,
      list_header=USE_DEFAULT, delete_row_confirm_question=USE_DEFAULT,
      hidden_filters=None, can_create_new=True, new_row_callback=None,
      saved_model_callback=None, deleted_model_callback=None,
      nav_css_class=None, show_column_headers=True, inline_create=False,
      inline_create_callback=None, margin_top_css=None,
      fetch_list_callback=None):

    self.js = []

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
            'query_key e.g. DateField(query_key=\'create_date__lte\')')

    self.display_columns = display_columns  # A list of DisplayColumns
    self.edit_field_names = edit_field_names or []  # A list of strings
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
            model._meta.verbose_name)
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
    self.show_column_headers = show_column_headers
    self.inline_create = inline_create
    self.inline_create_callback = inline_create_callback
    self.margin_top_css = margin_top_css or 'margin-top'
    self.fetch_list_callback = fetch_list_callback

  def add_js(self, js):
    self.js.append(js)

  def as_html(self):
    list_api_url = reverse(
        'list_or_save_new', kwargs={'model_name': self.model.__name__})
    # Otherwise this hands None to the template, which, being stupid, renders
    # 'None'
    label_edit_page_with_field = self.label_edit_page_with_field or ''

    # djaveCRUDTable/(crud_table.py (def __init__ args and body, as_html),
    # templates/(crud_table.html bottom of the page, js/crud_table.js
    # crud_table_options))
    context = {
        'list_api_url': list_api_url,
        'filter_widgets': self.filter_widgets,
        'hidden_filters': self.hidden_filters,
        'display_columns': self.display_columns,
        'show_column_headers': self.show_column_headers,
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
        'nav_css_class': self.nav_css_class or '',
        'inline_create': str(self.inline_create).lower(),
        'inline_create_callback': self.inline_create_callback or 'null',
        'margin_top_css': self.margin_top_css,
        'fetch_list_callback': self.fetch_list_callback or 'null',
        'js': mark_safe('\n'.join(self.js))}
    return render_to_string('crud_table.html', context)

  def new_button(self):
    if self.can_create_new and not self.inline_create:
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
