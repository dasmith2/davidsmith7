class DisplayInvoice(object):
  def __init__(self, invoice):
    self.invoice = invoice

  def as_html(self):
    return 'TODO: display {}'.format(self.invoice.invoice_id)
