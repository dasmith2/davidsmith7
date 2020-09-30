function saved_line_item_callback() {
  reload_invoices();
}

function deleted_line_item_callback() {
  reload_invoices();
}

function new_line_item_row_callback(row, model_data) {
  var type = model_data.line_item_type;
  if (type == 'projectlineitem') {
    row.find('.delete').text('Remove').addClass('remove');
  } else if (type == 'manuallineitem') {
    row.find('.amount_calculation textarea').remove();
  }
}
