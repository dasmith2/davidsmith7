""" This requires backbone.js and works together with crud_table.js to create
an html list that allows you to CRUD a filterable list of objects without any
page reloads.

If your table stays invisible, a likely culprit is that the browser's url
doesn't match the list_url. It's programmed to show the list and the edit panel
only when they match the browser's url. """
import json

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from djaveClassMagic.cases import (
    upper_case_singular, lower_case_singular, upper_case_plural,
    lower_case_plural)
from djaveHTML.a import AButton
from djaveHTML.field import Field
from djaveHTML.h import H1

from djaveCRUDTable.edit_model_table import EditModelTable
from djaveCRUDTable.filters import HIDDEN_NOT_DELETED_FILTER


USE_DEFAULT = 'USE_DEFAULT'


class CRUDTable(object):
  # djaveCRUDTable/(crud_table.py (def __init__ args and body, as_html),
  # templates/(crud_table.html bottom of the page, js/crud_table.js
  # crud_table_options))
  def __init__(
      self, model, display_columns, visible_filters=None,
      edit_field_names_or_rows=None, save_new_defaults=None,
      label_edit_page_with_field=None, list_url=None, details_url_root=None,
      list_api_url=None, list_header=USE_DEFAULT,
      confirm_delete_question=USE_DEFAULT, hidden_filters=USE_DEFAULT,
      can_create_new=True, nav_css_class=None, show_column_headers=True,
      inline_create=False, margin_top_css=None, new_button_text=None,
      global_reload_function_name=None, global_options_variable_name=None,
      footer_buttons=None,
      # function modified_row_callback(row, model_data, model) {}
      modified_row_callback=None,
      # saved_model_callback(new_project_data_or_whatever) {}
      saved_model_callback=None,
      # deleted_model_callback(backbone_model) {}
      deleted_model_callback=None,
      # inline_create_callback(model_data, create_row) {}
      inline_create_callback=None,
      # fetch_list_callback(models) {}
      fetch_list_callback=None,
      # edit_callback(details_panel, model_data) {}
      edit_callback=None):  # noqa: E129

    self.js = []

    self.model = model

    # A list of djaveHTML.field#Field
    self.visible_filters = visible_filters or []
    # A list of djaveHTML.field#HiddenField
    if hidden_filters == USE_DEFAULT:
      self.hidden_filters = [HIDDEN_NOT_DELETED_FILTER]
    else:
      self.hidden_filters = hidden_filters or []
    for filter_widget in self.visible_filters + self.hidden_filters:
      if not isinstance(filter_widget, Field):
        raise Exception(
            'Every filter widget and hidden filter must be a '
            'djaveHTML.field#Field, which {} isnt.'.format(filter_widget))
      if not filter_widget.additional_attrs.get('data-query-key', None):
        raise Exception(
            'Every filter widget and hidden filter must specify a '
            'query_key e.g. DateField(query_key=\'create_date__lte\'). You '
            'specified {}'.format(filter_widget.as_html()))

    self.display_columns = display_columns  # A list of DisplayColumns
    # A list of strings
    self.edit_field_names_or_rows = edit_field_names_or_rows or []
    # A dict, perhaps like {'user': 'me'}. These values get passed along to
    # /api/Project/2 or whatever when you save.
    self.save_new_defaults = save_new_defaults or {}
    # If you do 'name' and edit a Project (or whatever) whose name is
    # 'Exercise' then the edit panel will be titled "Edit Exercise" as opposed
    # to just "Edit project"
    self.label_edit_page_with_field = label_edit_page_with_field
    self.list_url = list_url or '/{}'.format(lower_case_plural(self.model))
    if list_header == USE_DEFAULT:
      list_header = H1([upper_case_plural(self.model)])
    elif isinstance(list_header, str):
      list_header = H1(list_header)
    self.list_header = list_header
    self.confirm_delete_question = ''
    if confirm_delete_question:
      if confirm_delete_question == USE_DEFAULT:
        self.confirm_delete_question = 'Delete this {}?'.format(
            model._meta.verbose_name)
      else:
        self.confirm_delete_question = confirm_delete_question
    self.can_create_new = can_create_new
    self.modified_row_callback = modified_row_callback
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
    self.new_button_text = new_button_text
    self.global_reload_function_name = global_reload_function_name
    self.details_url_root = details_url_root or self.list_url
    self.edit_callback = edit_callback
    self.list_api_url = list_api_url
    self.global_options_variable_name = global_options_variable_name
    self.footer_buttons = footer_buttons or []

  def add_js(self, js):
    if js.find('.js') > 0:
      raise Exception('You probably meant to call add_js_from_template')
    self.js.append(js)

  def add_js_from_template(self, js_template_path, request=None, **context):
    self.js.append(render_to_string(
        js_template_path, request=request, context=context))

  def as_html(self):
    list_api_url = self.list_api_url or reverse(
        'list_or_save_new', kwargs={'model_name': self.model.__name__})
    # Otherwise this hands None to the template, which, being stupid, renders
    # 'None'
    label_edit_page_with_field = self.label_edit_page_with_field or ''

    # djaveCRUDTable/(crud_table.py (def __init__ args and body, as_html),
    # templates/(crud_table.html bottom of the page, js/crud_table.js
    # crud_table_options))
    edit_table = EditModelTable(
        self.model, self.edit_field_names_or_rows, self.list_url)
    govn = self.global_options_variable_name or ''
    context = {
        'list_api_url': list_api_url,
        'visible_filters': self.visible_filters,
        'hidden_filters': self.hidden_filters,
        'display_columns': self.display_columns,
        'show_column_headers': self.show_column_headers,
        'edit_table': edit_table,
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
        'footer_buttons': self.get_footer_buttons(),
        'confirm_delete_question': self.confirm_delete_question,
        'modified_row_callback': self.modified_row_callback or 'null',
        'saved_model_callback': self.saved_model_callback or 'null',
        'deleted_model_callback': self.deleted_model_callback or 'null',
        'nav_css_class': self.nav_css_class or '',
        'inline_create': self.inline_create,
        'inline_create_js': str(self.inline_create).lower(),
        'inline_create_callback': self.inline_create_callback or 'null',
        'margin_top_css': self.margin_top_css,
        'fetch_list_callback': self.fetch_list_callback or 'null',
        'global_reload_function_name': self.global_reload_function_name or '',
        'details_url_root': self.details_url_root or self.list_url,
        'edit_callback': self.edit_callback or 'null',
        'global_options_variable_name': govn,
        'js': mark_safe('\n'.join(self.js))}
    return render_to_string('crud_table.html', context)

  def get_footer_buttons(self):
    to_return = []
    new_button = self.new_button()
    if new_button:
      to_return.append(new_button)
    to_return.extend(self.footer_buttons)
    return to_return

  def new_button(self):
    if self.can_create_new and not self.inline_create:
      new_button_text = self.new_button_text or (
          'New {}'.format(upper_case_singular(self.model)))
      new_button_url = '{}/0'.format(self.details_url_root)
      return AButton(
          new_button_text, new_button_url, css_classes=['createnew'])
