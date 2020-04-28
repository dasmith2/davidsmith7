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
  $.post(url, add_csrf_token(data), success);
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
