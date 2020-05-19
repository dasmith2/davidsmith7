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
    text_box_selector, action_url, text_field_name, success) {
  /* This is for text boxes in tables so you can edit names and descriptions
   * inline with AJAX. Once you start editing a text box, this hides all the
   * other buttons and gives the user a bogus "Save" button to click. Once the
   * text is actually saved due to the change event, remove the "Save" button
   * and put all the original buttons back. This ensures that we don't get a
   * race between the AJAX that this text box kicks off with the AJAX that
   * clicked buttons kick off. */
  var get_other_buttons = function(text_box) {
    return text_box.parents('tr').find('button,.button');
  };
  $(text_box_selector).keyup(function() {
    var text_box = $(this);
    var other_buttons = get_other_buttons(text_box).hide();
    var cell = other_buttons.parents('td');
    var bogus_save_button = cell.find('.bogus-save');
    if (!bogus_save_button.length) {
      bogus_save_button = $(
          '<button class="bogus-save" type="button">Save</button>');
      bogus_save_button.appendTo(cell).click(function() {
        $(this).prop('disabled', true);
      });
    }
    bogus_save_button.prop('disabled', false).show();
  }).change(function() {
    var text_box = $(this);
    var other_buttons = get_other_buttons(text_box);
    var cell = other_buttons.parents('td');
    var bogus_save_button = cell.find('.bogus-save');
    var pk = find_pk(text_box);
    var data = {pk: pk};
    data[text_field_name] = text_box.val()
    var feedback = get_feedback_elt_after(text_box);
    post(action_url, data, function(response) {
      if (!show_problem(response, feedback)) {
        other_buttons.show();
        bogus_save_button.hide();
        feedback.show().text('Saved!');
        if (success) {
          success();
        }
        window.setTimeout(function() {
          feedback.text('');
        }, 1000);
      }
    }).fail(function() {
      alert('Server error :(');
    });
  });
}
