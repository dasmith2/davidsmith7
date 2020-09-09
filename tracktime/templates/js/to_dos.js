function append_delete_button(row) {
  var html = '<button type="button" class="delete">Delete</button>';
  var button = $(html).appendTo(buttons_cell(row));
  space_out_buttons(row);
}

function remove_delete_button(row) {
  row.find('.delete').remove();
  space_out_buttons(row);
}

function new_to_do_row(row, model_data) {
  row.attr('data-done', Boolean(model_data.done) + '');
  setup_set_clear_dt_green_mode(
      row, 'done', 'Done', 'Not done', remove_delete_button,
      append_delete_button);
}

function inline_create_to_do_callback(model_data, create_row) {
  create_row.find('textarea').focus();
}
