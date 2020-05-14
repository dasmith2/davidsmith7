from abc import abstractmethod

from djaveTable.cell_content import CellContent


class FormElement(CellContent):
  """ A FormElement is a button or html input that can be rendered in the cell
  of a djaveTable, and when the form submits, the FormElement will be
  represented in the data that goes to the server. """
  def __init__(self, key_prefix, pk):
    self.key_prefix = key_prefix
    self.pk = pk

  def key(self):
    if self.key_prefix:
      if self.pk:
        return '{}_{}'.format(self.key_prefix, self.pk)
      return self.key_prefix
    return ''

  @abstractmethod
  def as_html(self):
    raise NotImplementedError('as_html')

  def __eq__(self, other):
    if self.__class__ != other.__class__:
      raise Exception('I do not know how to compare a {} to a {}'.format(
          self.__class__, other.__class__))
    return self.as_html() == other.as_html()

  def __repr__(self):
    return self.as_html()
