""" This stuff is for responsive design that tries to take the screen size and
the user's preferences into account when picking font sizes and such.

The difference between zoom and fit_to_screen is that zoom considers the user's
preference for an overriding zoom setting, while fit_to_screen ignores the zoom
override and simply fits to the screen. This is handy if you want the user to
be able to pick the zoom to change font sizes, but want the width of boxes to
always fill the screen. """
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def zoom(context, value):
  return calc_zoom(
      _automatic_zoom_factor(context.request),
      _overrize_zoom_factor(context), value)


@register.simple_tag(takes_context=True)
def fit_to_screen(context, value):
  return calc_zoom(_automatic_zoom_factor(context.request), None, value)


@register.simple_tag(takes_context=True)
def font_size(context, delta_factor=None):
  target = 21
  if delta_factor:
    target *= delta_factor
  px = calc_zoom(
      _automatic_zoom_factor(context.request), _overrize_zoom_factor(context),
      target)
  return '{}px'.format(px)


def calc_zoom(auto_zoom_factor, override_zoom_factor, value):
  if value == '':
    raise Exception(
        'Zoom gets an empty string when you accidentally do, like, '
        '{% zoom 1p %}')
  if value == 0:
    return value
  zoom_factor = 1
  if override_zoom_factor:
    zoom_factor = override_zoom_factor
  elif auto_zoom_factor:
    zoom_factor = auto_zoom_factor
  return max([1, int(zoom_factor * value)])


def _automatic_zoom_factor(request):
  str_value = request.GET.get('zoom', None)
  if str_value:
    return float(str_value)


def _overrize_zoom_factor(context):
  return context.get('override_zoom_factor', None)
