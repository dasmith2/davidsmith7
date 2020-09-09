function setup_edit_table_turns_yellow(table_finder) {
  /* This is used by the edit details panel to turn a field's row yellow when
   * you edit it. */
  $(table_finder).find('tbody tr').each(function() {
    setup_edit_row_turns_yellow($(this));
  });
}

function setup_edit_row_turns_yellow(
    row, turn_on_edit_mode_callback, turn_off_edit_mode_callback) {
  /* This is used by setup_edit_table_turns_yellow for the edit details panel,
   * but it's also used on each row in the list table for inline editing by
   * models_item_view.js The callbacks are basically to show and hide buttons.
   * */
  var elts = row.find('input,select,textarea');
  set_saved_values(elts);

  var handle_row_maybe_changed = function(event) {
    calc_edit_mode(
        row, turn_on_edit_mode_callback, turn_off_edit_mode_callback);
  };

  anything_happened(elts, handle_row_maybe_changed);
}

function set_saved_values(selector_or_elt) {
  $(selector_or_elt).each(function() {
    var elt = $(this);
    elt.attr('data-saved-value', val(elt));
  });
}

var calc_edit_mode = function(
    row, turn_on_edit_mode_callback, turn_off_edit_mode_callback) {
  var got_all_elts = all_elts(row);
  var any_editing = false;
  for (var i = 0; i < got_all_elts.length; i++) {
    any_editing = any_editing || is_editing($(got_all_elts[i]));
  }
  if (any_editing) {
    turn_on_edit_mode(row, turn_on_edit_mode_callback);
  } else {
    turn_off_edit_mode(row, turn_off_edit_mode_callback);
  }
};

function anything_happened(selector_or_elt, callback) {
  $(selector_or_elt).on('input', callback);
}

var all_elts = function(row) {
  // Wait to calculate this so all columns that want to edit get a chance
  // to wire up.
  return row.find('[data-saved-value]');
};

var is_editing = function(elt) {
  // Sometimes val(elt) is a boolean but I'm comparing it to a string version
  // of an earlier value.
  return elt.attr('data-saved-value') != (val(elt) + '');
};

var turn_on_edit_mode = function(row, turn_on_edit_mode_callback) {
  row.addClass('editing');
  if (turn_on_edit_mode_callback) {
    turn_on_edit_mode_callback(row);
  }
};

var turn_off_edit_mode = function(row, turn_off_edit_mode_callback) {
  row.removeClass('editing');
  if (turn_off_edit_mode_callback) {
    turn_off_edit_mode_callback(row);
  }
};
