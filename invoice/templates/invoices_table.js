function paid_success(pk) {
  var row = row_by_pk(pk);
  row.addClass('paid');
  row.removeClass('sent');
  row.find('.markpaid,.edit').remove();
  var data = {'pk': pk, 'type': 'Invoice'};
  post('{{ ajax_get_url }}', data, function(response) {
    row.find('.status_cell').text(response.status_with_date);
  });
}
wire_up_ajax_button('.markpaid', '{{ mark_invoice_paid_url }}', paid_success);
