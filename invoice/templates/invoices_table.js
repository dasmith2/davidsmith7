function paid_success(pk) {
  var row = row_by_pk(pk);
  row.addClass('paid');
  row.removeClass('sent');
  row.find('.markpaid,.edit').remove();
}
wire_up_ajax_button('.markpaid', '{{ mark_invoice_paid_url }}', paid_success);
