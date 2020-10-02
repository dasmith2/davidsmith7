function setup_set_clear_dt_green_mode(
    row, field_name, set_button_text, unset_button_text,
    set_mode_callback, unset_mode_callback) {
  /* You have a model where, when a field is set, the row should be colored
   * green, but when the field is not set, the row is uncolored. You need
   * buttons that switch between the modes and set the field to either now or
   * null. For instance, ToDos have a `done` field and invoices have a `paid`
   * field. */

  var set_mode = function() {
    row.addClass('green');
    var buttons = buttons_cell(row);
    buttons.find('.set').remove();
    // This code uses the .unset class, but the web tests probably find it
    // makes more sense to search for the .not_done button or whatever.
    var unset = $('<button type="button"></button>').text(
        unset_button_text).addClass('unset').addClass('not_' + field_name);

    unset.click(function() {
      _update_field(row, null, unset_mode);
    });

    buttons.prepend(unset);
    space_out_buttons(row);

    if (set_mode_callback) {
      set_mode_callback(row);
    }
  };

  var unset_mode = function() {
    row.removeClass('green');
    var buttons = buttons_cell(row);
    buttons.find('.unset').remove();
    // This code uses the .set class, but the web tests probably find it makes
    // more sense to search for the, like, .done button or whatever.
    var set = $('<button type="button"></button>').text(
        set_button_text).addClass('set').addClass(field_name);

    set.click(function() {
      _update_field(row, 'now', set_mode);
    });

    buttons.prepend(set);
    space_out_buttons(row);

    if (unset_mode_callback) {
      unset_mode_callback(row);
    }
  };

  var _update_field = function(row, new_value, success_accepts_pk) {
    var feedback = get_feedback_elt_append(buttons_cell(row));
    var pk = find_pk(row);
    var success = function() {
      success_accepts_pk(pk);
    };
    return update_field(
        find_model(row), pk, field_name, new_value, success, null, feedback);
  };

  if (buttons_cell(row).length == 0) {
    window.log_error('Unable to find the buttons cell for a row');
    return;
  }
  var field_data_attr = 'data-' + field_name;
  var field_data_val = row.attr(field_data_attr).toLowerCase();
  if (field_data_val != 'true' && field_data_val != 'false') {
    var message = (
        'These rows should have a True or False '
        + field_data_attr);
    // Don't throw message because then Firefox just hands blank information
    // to onerror.
    window.log_error(message);
    return;
  }
  var is_set = field_data_val == 'true';
  if (is_set) {
    set_mode(find_pk(row));
  } else {
    unset_mode(find_pk(row));
  }
}
