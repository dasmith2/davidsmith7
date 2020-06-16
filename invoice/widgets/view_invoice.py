from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from djaveDT import d_to_str, now
from djaveForm.button import Button

from invoice.widgets.view_line_items import ViewLineItems
from invoice.html_email_context import html_context


class ViewInvoice(object):
  def __init__(self, invoice, request):
    self.invoice = invoice
    self.request = request
    self.mark_sent_button = Button(
        'I will send this invoice today', button_type='submit',
        additional_attrs={'style': ''})

    if self.mark_sent_button.get_was_clicked(request.POST):
      self.invoice.sent = now()
      self.invoice.save()

    self.view_line_items = ViewLineItems(invoice)

  def as_html(self):
    invoice_date = None
    mark_sent_button = self.mark_sent_button.as_html()
    if self.invoice.sent:
      invoice_date = d_to_str(self.invoice.sent)
      mark_sent_button = None

    (service_dates_label, service_dates_str) = self._label_and_service_dates()
    due = None
    if self.invoice.due:
      due = d_to_str(self.invoice.due)
    context = {
        'service_dates_label': service_dates_label,
        'service_dates_str': service_dates_str,
        'invoice_id': self.invoice.invoice_id,
        'invoice_date': invoice_date,
        'due': due,
        'mark_sent_button': mark_sent_button,
        'sent_to': self._sent_to(),
        'make_payable_to': self._make_payable_to(),
        'view_line_items': self.view_line_items}
    context.update(html_context())
    return render_to_string('view_invoice.html', context, request=self.request)

  def _label_and_service_dates(self):
    service_dates_label = 'Service date'
    service_dates_str = d_to_str(self.invoice.service_from)
    if self.invoice.service_to != self.invoice.service_from:
      if self.invoice.service_to.year == self.invoice.service_from.year:
        service_dates_str = self.invoice.service_from.strftime('%b %d')
      service_dates_str = '{} to {}'.format(
          service_dates_str,
          d_to_str(self.invoice.service_to))
      service_dates_label += 's'
    return (service_dates_label, service_dates_str)

  def _sent_to(self):
    return self._new_line_to_br(self.invoice.sent_to)

  def _make_payable_to(self):
    return self._new_line_to_br(self.invoice.make_payment_to)

  def _new_line_to_br(self, str):
    return mark_safe(str.replace('\n', '<br>\n'))
