from django import template

from photos.file_types import VALID_IMAGE_TYPES


register = template.Library()


@register.simple_tag
def valid_image_types():
  # Hack: this spits out valid Javascript.
  return str(VALID_IMAGE_TYPES)
