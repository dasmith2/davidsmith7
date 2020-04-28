function get_feedback_elt_after(after) {
  var feedback = after.parent().find('.feedback');
  if (!feedback.length) {
    feedback = $('<span class="feedback"></span>').insertAfter(after);
  }
  return feedback;
}

function get_feedback_elt_append(append) {
  var feedback = append.find('.feedback');
  if (!feedback.length) {
    feedback = $('<span class="feedback"></span>').appendTo(append);
  }
  return feedback;
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
