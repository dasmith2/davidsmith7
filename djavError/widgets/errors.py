from django.shortcuts import reverse
from djaveCRUDTable.columns import DisplayFieldColumn
from djaveHTML.a import AButton

from djavError.models.error import Error
from djavError.widgets.fixables import Fixables


class Errors(Fixables):
  def get_model(self):
    return Error

  def get_leading_columns(self):
    return [DisplayFieldColumn('Title')]

  def get_extra_buttons(self):
    return [AButton('View', reverse('see_error', kwargs={'pk': 'pk'}))]
