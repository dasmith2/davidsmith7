from django.shortcuts import reverse
from django.template import loader
from djaveAPI.models.api_key import username_available
from djaveTable.table import Table
from djaveForm.button import Button
from djaveForm.field import SlugField
from djaveForm.form import Form


class NewAPIKeyWidget(object):
  def __init__(self, request, new_api_key_table, title, description):
    self.request = request
    self.new_api_key_table = new_api_key_table
    self.title = title
    self.description = description

  def __str__(self):
    template = loader.get_template('new_api_key_widget.html')
    context = {
        'new_api_key_table': self.new_api_key_table,
        'delete_api_key_url': reverse('delete_key'),
        'title': self.title,
        'description': self.description}
    return template.render(context, request=self.request)


class NewAPIKeyForm(Form):
  def __init__(self):
    self.username_field = SlugField('username', required=True)
    self.save_button = Button('Save', button_type='submit')
    super().__init__([self.username_field, self.save_button])

  def is_valid(self):
    return super().is_valid() and (
        username_available(self.username_field.get_value()))


class NewAPIKeyTable(Table):
  def __init__(self, request_POST):
    super().__init__([
        'API Key username', 'API Key password', 'Webhook URL', ''])
    self.form = NewAPIKeyForm()
    keys = list(self.existing_keys())

    if request_POST:
      self.form.set_form_data(request_POST)
      if self.form.is_valid():
        new_api_key = self.create_key(self.form.username_field.get_value())
        keys = [new_api_key] + keys
        self.form = NewAPIKeyForm()

    self.setup_top_row()
    self.setup_keys_rows(keys)

  def setup_top_row(self):
    self.create_row([self.form.username_field, '', self.form.save_button])

  def setup_keys_rows(self, keys):
    for key in keys:
      password = '(Hidden forever)'
      if key.has_plain_password():
        password = (
            'Write this down because you\'ll never see it again:<br><br>'
            '<b>{}</b>').format(key.get_plain_password())
      self.create_row([key.username, password, Button('Delete')], pk=key.pk)

  def existing_keys(self):
    raise NotImplementedError('existing_keys')

  def create_key(self, username):
    raise NotImplementedError('existing_keys')
