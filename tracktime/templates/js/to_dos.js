function show_delete_button(row) {
  row.find('.delete').show();
  space_out_buttons(row);
}

function hide_delete_button(row) {
  row.find('.delete').hide();
  space_out_buttons(row);
}

function new_to_do_row(row, model_data) {
  row.attr('data-done', Boolean(model_data.done) + '');
  setup_set_clear_dt_green_mode(
      row, 'done', 'Done', 'Not done', hide_delete_button,
      show_delete_button);
}

function inline_create_to_do_callback(model_data, create_row) {
  create_row.find('textarea').focus();
}
