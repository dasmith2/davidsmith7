from django.template.loader import render_to_string
from djaveForm.button import Button
from djaveForm.field import HiddenField
from djaveForm.form import Form
from djaveStyle.models import get_zoom_override, set_zoom_override


ZOOM_CHANGE_FACTOR = 1.05  # Bump it up or down by 5%


class ZoomForm(Form):
  def __init__(self, user, request_POST):
    self.hidden_automatic_zoom = HiddenField('hiddenautomaticzoom')
    self.zoom_in_button = Button('Zoom in', button_type='submit')
    self.zoom_out_button = Button('Zoom out', button_type='submit')
    self.automatic_button = Button('Automatic', button_type='submit')
    super().__init__([
        self.hidden_automatic_zoom, self.zoom_in_button, self.zoom_out_button,
        self.automatic_button])

    self.things_happened = (
        request_POST and self.a_button_was_clicked(request_POST))
    if self.things_happened:
      self.set_form_data(request_POST)
      if self.zoom_in_button.get_was_clicked():
        set_zoom_override(user, ZOOM_CHANGE_FACTOR * self.current_zoom(user))
      elif self.zoom_out_button.get_was_clicked():
        set_zoom_override(user, self.current_zoom(user) / ZOOM_CHANGE_FACTOR)
      elif self.automatic_button.get_was_clicked():
        set_zoom_override(user, None)

  def current_zoom(self, user):
    return get_zoom_override(user) or float(
        self.hidden_automatic_zoom.get_value())


class ZoomPreference(object):
  def __init__(self, request, request_POST, user):
    self.request = request
    self.user = user
    self.form = ZoomForm(user, request_POST)

  def as_html(self):
    zoom_override = get_zoom_override(self.user)
    if zoom_override:
      zoom_override = round(zoom_override, 2)
    context = {'form': self.form, 'zoom_override': zoom_override}
    return render_to_string(
        'zoom_preference.html', context, request=self.request)
