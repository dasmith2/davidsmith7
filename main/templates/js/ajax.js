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
