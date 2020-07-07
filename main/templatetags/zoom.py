from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def zoom(context, value):
  return zoom_by_request(context.request, value)


def zoom_by_request(request, value):
  if value == '':
    raise Exception(
        'Zoom gets an empty string when you accidentally do, like, '
        '{% zoom 1p %}')
  if value == 0:
    return value
  zoom_factor = 1
  min_dimension = request.GET.get('min_dimension', None)
  if min_dimension:
    zoom_factor = int(min_dimension) / 600.0
  return max([1, int(zoom_factor * value)])
