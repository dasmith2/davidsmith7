/* Stuff that comes up when I'm enabling tables for AJAX */

function find_pk($element) {
  // Search up the dom for a data-pk attribute. So you might do something like
  // my_button.click(function() { var pk = find_pk($(this)); });
  if ($element.attr('data-pk')) {
    return $element.attr('data-pk');
  }
  return $element.parents('[data-pk]').attr('data-pk');
}

function find_model($element) {
  if ($element.attr('data-model')) {
    return $element.attr('data-model');
  }
  return $element.parents('[data-model]').attr('data-model');
}

function row_by_pk(pk) {
  return $('tr[data-pk=' + pk + ']');
}

function remove_row(pk) {
  var row = row_by_pk(pk);
  var table = row.parents('table');
  row.remove();
  if (!table.find('tbody tr').length) {
    $('<p class="margin-top">Nothing to report</p>').insertAfter(table);
    table.hide();
  }
}

function wire_up_click_updates_field(
    selector, field_name, new_value, success, confirm_question) {
  $(selector).click(function() {
    var button = $(this).prop('disabled', true);
    var always = function() {
      button.prop('disabled', false);
    };
    if (!confirm_question || confirm(confirm_question)) {
      var model = find_model(button);
      var pk = find_pk(button);
      var feedback = get_feedback_elt_after(button);
      update_field(
          model, pk, field_name, new_value, success, always, feedback);
    } else {
      always();
    }
  });
}

function wire_up_ajax_delete_button(selector_or_elt, confirm_question) {
  wire_up_click_updates_field(
      selector_or_elt, 'deleted', 'now', remove_row, confirm_question);
}

var all_elts = function(row) {
  // Wait to calculate this so all columns that want to edit get a chance
  // to wire up.
  return row.find('[data-saved-value]');
};

var other_buttons = function(row) {
  return row.find('button,.button');
};

var buttons_cell = function(row) {
  var by_other_buttons = other_buttons(row).parents('td');
  if (by_other_buttons.length) {
    return by_other_buttons;
  }
  return row.find('.buttons');
};

var turn_on_edit_mode = function(row) {
  other_buttons(row).hide();
  buttons_cell(row).find('.save-row,.cancel-save-row').show().prop(
      'disabled', false);
  row.addClass('editing');
};

var SAVED = 'Saved!';

var turn_off_edit_mode = function(row) {
  other_buttons(row).show();
  buttons_cell(row).find('.save-row,.cancel-save-row').hide();
  row.removeClass('editing');
  // Maybe you tried to blank out a field, hit save, got a required error,
  // typed your original back in, that turns off edit mode, but we should now
  // hide the required message. On the other hand, if you just successfully
  // clicked save, we don't want to instantly remove the "Saved!" message.
  row.find('.feedback').each(function() {
    if ($(this).text() != SAVED) {
      $(this).hide();
    }
  });
};

var calc_edit_mode = function(row) {
  var got_all_elts = all_elts(row);
  var any_editing = false;
  for (var i = 0; i < got_all_elts.length; i++) {
    any_editing = any_editing || is_editing($(got_all_elts[i]));
  }
  if (any_editing) {
    turn_on_edit_mode(row);
  } else {
    turn_off_edit_mode(row);
  }
};

var is_editing = function(elt) {
  return elt.attr('data-saved-value') != elt.val()
};

function wire_up_ajax_save_field(selector_or_elt, field_name) {
  /* This is for text boxes or whatever in tables so you can edit inline with
   * AJAX. Once you start editing, this hides all the other buttons and gives
   * the user "Save" and "Cancel" buttons. selector_or_elt can be a string or a
   * jQuery object. Closures are a little tricky here because I want the same
   * save button to save all editing fields. */
  $(selector_or_elt).each(function() {
    var elt = $(this);
    elt.attr('data-saved-value', elt.val());
    elt.attr('data-field-name', field_name);
  });

  var handle_row_maybe_changed = function(event) {
    /* This is, like, an on_change event for the entire row. Element level
     * stuff should be done in a loop over all_elts. */
    var row = $(this).parents('tr');
    var save_button = buttons_cell(row).find('.save-row');
    var cancel_save_button = buttons_cell(row).find('.cancel-save-row');

    if (!save_button.length) {
      var save_html = '<button class="save-row" type="button">Save</button>';
      save_button = $(save_html).appendTo(buttons_cell(row)).hide();
      var cancel_html =
          '<button class="cancel-save-row" type="button">Cancel</button>';
      cancel_save_button = $(cancel_html).appendTo(buttons_cell(row)).hide();

      save_button.click(function() {
        save_button.prop('disabled', true);
        cancel_save_button.prop('disabled', true);

        var data = {pk: find_pk(row), type: find_model(row)};

        var got_all_elts = all_elts(row);
        var first_feedback = null;
        var last_edited_elt = null;
        for (var i = 0; i < got_all_elts.length; i++) {
          var elt = $(got_all_elts[i]);
          if (is_editing(elt)) {
            if (first_feedback === null) {
              first_feedback = get_feedback_elt_after(elt);
            }
            data[elt.attr('data-field-name')] = elt.val()
            last_edited_elt = elt;
          }
        }

        var handle_elt_was_saved = function(elt) {
          var feedback = get_feedback_elt_after(elt);
          feedback.show().text(SAVED);
          elt.attr('data-saved-value', elt.val());
          window.setTimeout(function() {
            feedback.text('');
          }, 1000);
        };

        var success = function(response) {
          if (!show_problem(response, first_feedback)) {
            for (var i = 0; i < got_all_elts.length; i++) {
              var elt = $(got_all_elts[i]);
              if (is_editing(elt)) {
                handle_elt_was_saved(elt);
              }
            }
            // The save button disappears and you lose your tab location
            // otherwise.
            last_edited_elt.focus();
          }
          calc_edit_mode(row);
        };
        // DON'T use update_field here because data may have multiple fields.
        post('{{ ajax_update_url }}', data, success, null, first_feedback);
      });

      cancel_save_button.click(function() {
        row.find('.feedback').hide();
        var got_all_elts = all_elts(row);
        for (var i = 0; i < got_all_elts.length; i++) {
          var elt = $(got_all_elts[i]);
          elt.val(elt.attr('data-saved-value'));
        }
        calc_edit_mode(row);
      });
    }

    /* Actually respond to the event. */
    calc_edit_mode(row);
  };

  $(selector_or_elt).keyup(handle_row_maybe_changed);
  $(selector_or_elt).click(handle_row_maybe_changed);
}

function setup_set_clear_dt_green_mode(
    table_finder, field_name, set_button_text, unset_button_text,
    set_mode_callback, unset_mode_callback) {
  /* You have a model where, when a field is set, the row should be colored
   * green, but when the field is not set, the row is uncolored. You need
   * buttons that switch between the modes and set the field to either now or
   * null. For instance, ToDos have a `done` field and invoices have a `paid`
   * field. */

  var set_mode = function(row) {
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

    buttons.append(unset);

    if (set_mode_callback) {
      set_mode_callback(row);
    }
  };

  var unset_mode = function(row) {
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

    buttons.append(set);

    if (unset_mode_callback) {
      unset_mode_callback(row);
    }
  };

  var _update_field = function(row, new_value, success) {
    var feedback = get_feedback_elt_append(buttons_cell(row));
    update_field(
        find_model(row), find_pk(row), field_name, new_value, success,
        feedback);
  };

  var rows = $(table_finder).find('tr[data-pk]');
  for (var i = 0; i < rows.length; i++) {
    // I used a for loop so if I throw an exception the loop stops.
    var row = $(rows[i]);
    if (buttons_cell(row).length == 0) {
      window.log_error(
          'Unable to find the buttons cell for a row in ' + table_finder);
      return;
    }
    var field_data_attr = 'data-' + field_name;
    var field_data_val = row.attr(field_data_attr);
    if (field_data_val != 'True' && field_data_val != 'False') {
      var message = (
          table_finder + ' rows should have a True or False '
          + field_data_attr);
      // Don't throw message because then Firefox just hands blank information
      // to onerror.
      window.log_error(message);
      return;
    }
    var is_set = field_data_val == 'True';
    if (is_set) {
      set_mode(row);
    } else {
      unset_mode(row);
    }
  }
}
