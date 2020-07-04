function set_status(row) {
  var data = {'pk': find_pk(row), 'type': 'Invoice'};
  post('{{ ajax_get_url }}', data, function(response) {
    row.find('.status_cell').text(response.status_with_date);
  });
}

function append_edit_button(row) {
  var view_button = buttons_cell(row).find('.view');
  var button = $('<a class="edit button">Edit</a>').attr(
      'href', row.attr('data-edit-url')).insertAfter(view_button);
  row.addClass(row.attr('data-class-if-not-paid'));
  set_status(row);
}

function remove_edit_button(row) {
  row.find('.edit').remove();
  row.removeClass(row.attr('data-class-if-not-paid'));
  set_status(row);
}

function init_paid_mode() {
  var table_finder = 'table[data-model="Invoice"]';
  var field_name = 'paid';
  var set_mode_callback = remove_edit_button;
  var unset_mode_callback = append_edit_button;
  setup_set_clear_dt_green_mode(
      table_finder, field_name, 'Paid', 'Not paid',
      set_mode_callback, unset_mode_callback);
}
$(init_paid_mode);
