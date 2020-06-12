/* AJAX stuff */
function ok(response) {
  return response['OK'];
}

function show_problem(response, feedback_or_append_to) {
  var feedback;
  if (feedback_or_append_to.hasClass('feedback')) {
    feedback = feedback_or_append_to;
  } else {
    feedback = get_feedback_elt_append(feedback_or_append_to);
  }
  var problem = problem_in_response(response);
  if (problem) {
    feedback.text(problem).show();
    return true;
  } else {
    feedback.hide();
    return false;
  }
}

function problem_in_response(response) {
  if (response.responseJSON) {
    // You need this for .fail(function(response) { ...
    response = response.responseJSON;
  }
  return response['problem'];
}

function post(url, data, success) {
  return $.post(url, add_csrf_token(data), success).fail(function(response) {
    console.log(problem_in_response(response));
  });
}

/* csrf token stuff */
function add_csrf_token(data) {
  data['csrfmiddlewaretoken'] = get_csrf_token();
  return data;
}

function before_send_delete() {
  // https://stackoverflow.com/questions/13089613/ajax-csrf-and-delete
  return function(xhr) {
    xhr.setRequestHeader("X-CSRFToken", get_csrf_token());
  };
}

function get_csrf_token() {
  return $('input[name=csrfmiddlewaretoken]').val();
}

/* Stuff that comes up when I'm enabling tables for AJAX */

function find_id($element) {
  // Search up the dom for a data-id attribute. So you might do something like
  // my_button.click(function() { var id = find_id($(this)); });
  if ($element.attr('data-id')) {
    return $element.attr('data-id');
  }
  return $element.parents('[data-id]').attr('data-id');
}

function find_model($element) {
  if ($element.attr('data-model')) {
    return $element.attr('data-model');
  }
  return $element.parents('[data-model]').attr('data-model');
}

function row_by_pk(id) {
  return $('tr[data-id=' + id + ']');
}

function remove_row(id) {
  row_by_pk(id).remove();
}

function wire_up_ajax_button(
    selector_or_elt, action_url, success, confirm_question) {
  /* This is for buttons in tables where it's, like, one object per row, and
   * the user can click buttons that do things to the objects. confirm_question
   * is optional and is, like, 'Are you sure you want to delete this whatever?'
   * selector_or_elt can be a string or a jQuery object. */
  $(selector_or_elt).click(function() {
    var button = $(this).prop('disabled', true);
    window.delete_button = button; // DO NOT SUBMIT
    var model = find_model(button);
    var buttons_cell = button.parents('td');
    var id = find_id(button);
    var post_data = {id: id, type: model};
    if (!confirm_question || confirm(confirm_question)) {
      post(action_url, post_data, function(response) {
        if (!show_problem(response, buttons_cell)) {
          success(id);
        }
        button.prop('disabled', false);
      }).fail(function(data) {
        button.prop('disabled', false);
      });
    } else {
      button.prop('disabled', false);
    }
  });
}

function wire_up_ajax_delete_button(selector_or_elt, confirm_question) {
  wire_up_ajax_button(
      selector_or_elt, '{{ ajax_delete_url }}', remove_row, confirm_question);
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
  return other_buttons(row).parents('td');
};

var turn_on_edit_mode = function(row) {
  other_buttons(row).hide();
  buttons_cell(row).find('.save-field,.cancel-save-field').show().prop(
      'disabled', false);
  row.addClass('editing');
};

var SAVED = 'Saved!';

var turn_off_edit_mode = function(row) {
  other_buttons(row).show();
  buttons_cell(row).find('.save-field,.cancel-save-field').hide();
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
    var save_button = buttons_cell(row).find('.save-field');
    var cancel_save_button = buttons_cell(row).find('.cancel-save-field');

    if (!save_button.length) {
      var save_html = '<button class="save-field" type="button">Save</button>';
      save_button = $(save_html).appendTo(buttons_cell(row)).hide();
      var cancel_html =
          '<button class="cancel-save-field" type="button">Cancel</button>';
      cancel_save_button = $(cancel_html).appendTo(buttons_cell(row)).hide();

      save_button.click(function() {
        save_button.prop('disabled', true);
        cancel_save_button.prop('disabled', true);

        var data = {id: find_id(row), type: find_model(row)};

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

        post('{{ ajax_update_url }}', data, function(response) {
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
        }).fail(function(response) {
          window.response = response; // DO NOT SUBMIT
          if (!show_problem(response, first_feedback)) {
            first_feedback.show().text('Server error :(');
          }
        });
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
