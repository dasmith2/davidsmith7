function get_feedback_elt_after(after) {
  if (typeof after == 'string') {
    after = $(after);
  }
  var feedback = after.parent().find('.feedback');
  if (!feedback.length) {
    feedback = $('<span class="feedback"></span>').insertAfter(after);
  }
  return feedback;
}

function get_feedback_elt_append(append) {
  if (typeof append == 'string') {
    append = $(append);
  }
  var feedback = append.find('.feedback');
  if (!feedback.length) {
    feedback = $('<span class="feedback"></span>').appendTo(append);
  }
  return feedback;
}
