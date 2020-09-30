function show_edit_mode_buttons(row, saved_callback) {
  if (row.attr('data-pk')) {
    init_edit_mode_buttons(row, saved_callback);
    var save_cancel_buttons = buttons_cell(row).find(
        '.save-row,.cancel-save-row');
    other_buttons(row).hide();
    save_cancel_buttons.show().prop('disabled', false);
  }
}

var SAVED = 'Saved!';

function show_original_buttons(row) {
  if (row.attr('data-pk')) {
    other_buttons(row).show();
    buttons_cell(row).find('.save-row,.cancel-save-row').hide();
    // Maybe you tried to blank out a field, hit save, got a required error,
    // typed your original back in, that turns off edit mode, but we should now
    // hide the required message. On the other hand, if you just successfully
    // clicked save, we don't want to instantly remove the "Saved!" message.
    row.find('.feedback').each(function() {
      if ($(this).text() != SAVED) {
        $(this).hide();
      }
    });
  }
}

function init_edit_mode_buttons(row, saved_callback) {
  var save_button = buttons_cell(row).find('.save-row');
  var cancel_button = buttons_cell(row).find('.cancel-save-row');

  if (!save_button.length) {
    var save_html = '<button class="save-row" type="button">Save</button>';
    save_button = $(save_html).appendTo(buttons_cell(row)).hide();
    var cancel_html =
        '<button class="cancel-save-row" type="button">Cancel</button>';
    cancel_button = $(cancel_html).appendTo(buttons_cell(row)).hide();

    save_button.click(function() {
      save_button.prop('disabled', true);
      cancel_button.prop('disabled', true);

      var data = {};

      var got_all_elts = all_elts(row);
      var first_feedback = null;
      var last_edited_elt = null;
      for (var i = 0; i < got_all_elts.length; i++) {
        var elt = $(got_all_elts[i]);
        if (is_editing(elt)) {
          if (first_feedback === null) {
            first_feedback = get_feedback_elt_after(elt);
          }
          data[elt.attr('name')] = elt.val()
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
        calc_edit_mode_4_edit_list_table(row);
        if (saved_callback) {
          saved_callback();
        }
      };
      // DON'T use update_field here because data may have multiple fields.
      var url = options.base_api_url + '/' + find_pk(row);
      post(url, data, success, null, first_feedback);
    });

    cancel_button.click(function() {
      row.find('.feedback').hide();
      var got_all_elts = all_elts(row);
      for (var i = 0; i < got_all_elts.length; i++) {
        var elt = $(got_all_elts[i]);
        elt.val(elt.attr('data-saved-value'));
        if (elt[0].tagName == 'TEXTAREA') {
          resize_textarea(elt);
        }
      }
      calc_edit_mode_4_edit_list_table(row);
    });
  }
}

function calc_edit_mode_4_edit_list_table(row) {
  calc_edit_mode(row, show_edit_mode_buttons, show_original_buttons);
}
