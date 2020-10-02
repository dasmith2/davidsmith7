function show_other_buttons(row) {
  row.find('.delete,.top').show();
  space_out_buttons(row);
}

function hide_other_buttons(row) {
  row.find('.delete,.top').hide();
  space_out_buttons(row);
}

function modified_to_do_row(row, model_data, model) {
  var done = Boolean(model_data.done);
  row.attr('data-done', done + '');
  var done = function() {
    hide_other_buttons(row);
  };
  var not_done = function() {
    show_other_buttons(row);
  };
  setup_set_clear_dt_green_mode(
      row, 'done', 'Done', 'Not done', done, not_done);

  var top_button = row.find('.top');
  var pk = model.get('id');
  var current_timestamp = function() {
    return Math.round(Date.now() / 1000);
  };
  var success = function() {
    var tbody = row.parents('.list-table tbody');
    row.remove().prependTo(tbody);
  };
  button_updates_field(
      top_button, 'ToDo', pk, 'sort_timestamp', current_timestamp, success);
}

function inline_create_to_do_callback(model_data, create_row) {
  create_row.find('textarea').focus();
}
