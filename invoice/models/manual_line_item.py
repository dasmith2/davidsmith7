from invoice.models.line_item import LineItem


class ManualLineItem(LineItem):
  @classmethod
  def model_description(cls):
    return (
        'A ManualLineItem is added manually to an Invoice, typically by a '
        'human. It\'s useful for when you have some random thing you need to '
        'bill for.')
