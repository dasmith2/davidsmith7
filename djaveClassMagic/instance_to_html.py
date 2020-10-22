""" This is the quickest and simplest way to turn an instance into a readonly
html display. """

from django.contrib.auth.models import User
from djaveHTML.a import A
from djaveHTML.h import H1
from djaveHTML.table import Table
from djaveHTML.wrapper import Wrapper

from djaveClassMagic.model_fields import model_fields


def instance_to_html(instance):
  """ This just does the fields of the instance. It doesn't know about related
  objects. """
  header = H1('{}'.format(str(instance)))

  table = Table(['Field', 'Value'], css_classes='margin-top-half')
  for field in model_fields(instance.__class__):
    if field.foreign_key_to:
      foreign_obj = getattr(instance, field.name)
      if field.foreign_key_to is User:
        # Yet another special case for django user.
        value = foreign_obj.username
      else:
        if not hasattr(foreign_obj, 'url'):
          raise Exception((
              'In order for instance_to_html to work on a {}, it has to '
              'implement def url(self)').format(field.foreign_key_to))
        value = A(str(foreign_obj), foreign_obj.url()).to_html()
    else:
      value = field.value_as_str(instance)
    table.create_row([field.name, value])

  return Wrapper(header, table)
