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
  if (response['problem']) {
    feedback.text(response['problem']).show();
    return true;
  } else {
    feedback.hide();
    return false;
  }
}

function post(url, data, success) {
  return $.post(url, add_csrf_token(data), success).fail(function() {
    alert('Server error :(');
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

function find_pk($element) {
  // Search up the dom for a data-pk attribute. So you might do something like
  // my_button.click(function() { var pk = find_pk($(this)); });
  if ($element.attr('data-pk')) {
    return $element.attr('data-pk');
  }
  return $element.parents('[data-pk]').attr('data-pk');
}

function row_by_pk(pk) {
  return $('tr[data-pk=' + pk + ']');
}

function remove_row(pk) {
  row_by_pk(pk).remove();
}

function wire_up_ajax_button(selector, action_url, success, confirm_question) {
  /* This is for buttons in tables where it's, like, one object per row, and
   * the user can click buttons that do things to the objects. confirm_question
   * is optional and is, like, 'Are you sure you want to delete this whatever?'
   * */
  $(selector).click(function() {
    var button = $(this).prop('disabled', true);
    var cell = button.parents('td');
    var pk = find_pk(button);
    var post_data = {'pk': pk};
    if (!confirm_question || confirm(confirm_question)) {
      post(action_url, post_data, function(response) {
        if (!show_problem(response, cell)) {
          success(pk);
        }
        button.prop('disabled', false);
      }).fail(function(data) {
        alert('Server error :(');
        button.prop('disabled', false);
      });
    } else {
      button.prop('disabled', false);
    }
  });
}

function wire_up_ajax_save_text(
    text_box_selector, action_url, text_field_name, success_callback) {
  /* This is for text boxes in tables so you can edit names and descriptions
   * inline with AJAX. Once you start editing a text box, this hides all the
   * other buttons and gives the user "Save" and "Cancel" buttons. */
  var get_other_buttons = function(text_box) {
    return text_box.parents('tr').find('button,.button');
  };
  $(text_box_selector).each(function() {
    var text_box = $(this);
    text_box.attr('data-saved-text', text_box.val());
  });
  $(text_box_selector).keyup(function(event) {
    /* Make sure all the buttons, variables, and functions are set up */
    var text_box = $(this);
    var feedback = get_feedback_elt_after(text_box);
    var other_buttons = get_other_buttons(text_box);
    var cell = other_buttons.parents('td');
    var save_text_button = cell.find('.save-text');
    var cancel_save_text_button = cell.find('.cancel-save-text');

    var turn_on_edit_text_mode = function() {
      other_buttons.hide();
      cell.find('.save-text,.cancel-save-text').show().prop('disabled', false);
    };

    var turn_off_edit_text_mode = function() {
      other_buttons.show();
      cell.find('.save-text,.cancel-save-text').hide();
    };

    if (!save_text_button.length) {
      var save_html = '<button class="save-text" type="button">Save</button>';
      save_text_button = $(save_html).appendTo(cell).hide();
      var cancel_html =
          '<button class="cancel-save-text" type="button">Cancel</button>';
      cancel_save_text_button = $(cancel_html).appendTo(cell).hide();

      save_text_button.click(function() {
        save_text_button.prop('disabled', true);
        cancel_save_text_button.prop('disabled', true);
        var pk = find_pk(text_box);
        var data = {pk: pk};
        data[text_field_name] = text_box.val()
        post(action_url, data, function(response) {
          if (!show_problem(response, feedback)) {
            turn_off_edit_text_mode();
            feedback.show().text('Saved!');
            text_box.attr('data-saved-text', text_box.val());
            if (success_callback) {
              success_callback();
            }
            // The save button disappears and you lose your tab location
            // otherwise.
            text_box.focus();
            window.setTimeout(function() {
              feedback.text('');
            }, 1000);
          }
        }).fail(function() {
          feedback.show().text('Server error :(');
        });
      });

      cancel_save_text_button.click(function() {
        text_box.val(text_box.attr('data-saved-text'));
        turn_off_edit_text_mode();
      });
    }

    /* Actually respond to the event. */
    if (text_box.attr('data-saved-text') == text_box.val()) {
      turn_off_edit_text_mode();
    } else {
      turn_on_edit_text_mode();
    }
  });
}
