function set_status(row) {
  // Otherwise it runs one AJAX query per row when the page loads. I only want
  // to run the status fetching AJAX query if something changed.
  var init_finder = 'data-status-initialized';
  if (row.attr(init_finder)) {
    var url = '{{ list_invoice_api_url }}/' + find_pk(row);
    get(url, function(response) {
      row.find('.status_cell').text(response.status_with_date);
    });
  } else {
    row.attr(init_finder, true);
  }
}

function set_unpaid_mode(row) {
  var view_button = buttons_cell(row).find('.view');
  var button = $('<a class="edit button">Edit</a>').attr(
      'href', row.attr('data-edit-url')).insertAfter(view_button);
  row.addClass(row.attr('data-class-if-not-paid'));
  set_status(row);
  if (row.hasClass('created')) {
    row.find('.paid').remove();
  }
}

function set_paid_mode(row) {
  row.find('.edit').remove();
  row.removeClass(row.attr('data-class-if-not-paid'));
  set_status(row);
}

function init_paid_mode() {
  var table_finder = 'table[data-model="Invoice"]';
  var field_name = 'paid';
  var set_mode_callback = set_paid_mode;
  var unset_mode_callback = set_unpaid_mode;
  setup_set_clear_dt_green_mode(
      table_finder, field_name, 'Paid', 'Not paid',
      set_mode_callback, unset_mode_callback);
}
$(init_paid_mode);
