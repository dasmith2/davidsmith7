from invoice.models.line_item import LineItem


class ManualLineItem(LineItem):
  """ A Manual Line Item is simply typed in manually by a human. It's a useful
  for when you have some random thing you need to bill for. """
  pass
