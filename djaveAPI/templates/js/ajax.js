/* AJAX stuff */
function ok(response) {
  return response['OK'];
}

function show_problem(response, feedback_or_append_to) {
  var feedback;
  if (!feedback_or_append_to) {
    feedback = default_feedback();
  } else if (feedback_or_append_to.hasClass('feedback')) {
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

function feedback_or_default(feedback) {
  return feedback || default_feedback();
}

function default_feedback() {
  return get_feedback_elt_append('body');
}

function problem_in_response(response) {
  if (response.responseJSON) {
    // You need this for .fail(function(response) { ...
    response = response.responseJSON;
  } else if (
      response.status && typeof response.status == 'number'
      && response.status != 200) {
    // When objects have a status, it's a word. When responses have a failed
    // status, it's a number.
    if (response.status == 403) {
      return 'Hm, it looks like your login changed. Try refreshing the page.';
    }
    return response.status;
  }
  return response['problem'];
}

function ajax_delete(url, success, always, feedback) {
  var request_obj = $.ajax({
      url: url,
      type: 'DELETE',
      success: _success_callback(success, always, feedback)});
  _add_fail(request_obj, always, feedback);
}

function post(url, data, success, always, feedback) {
  var success_callback = _success_callback(success, always, feedback);
  // Not every site I build uses single-page. In a single-page scenario, the
  // right time to call wire_up_ajax_csrf would be right after the logged in
  // user changed. But by putting it here I cover all cases.
  wire_up_ajax_csrf();
  var request_obj = $.post(url, data, success_callback);
  _add_fail(request_obj, always, feedback);
}

$(wire_up_ajax_csrf);

function get(url, success, always, feedback) {
  var success_callback = _success_callback(success, always, feedback);
  var request_obj = $.get(url, success_callback);
  _add_fail(request_obj, always, feedback);
  return request_obj;
}

function _success_callback(success, always, feedback) {
  return function(response) {
    if (!show_problem(response, feedback)) {
      if (success) {
        success(response);
      }
    }
    if (always) {
      always();
    }
  }
}

function _add_fail(request_obj, always, feedback) {
  request_obj.fail(function(response) {
    if (!show_problem(response, feedback)) {
      if (response.status == 0 && response.statusText == 'error') {
        // Firefox is complaining because somebody closed the window before the
        // response could come back and be handled.
        return
      }
      feedback_or_default(feedback).show().text('Server error :(');
      console.log('Server error :(');
      window.onerror(
          'AJAX request got a server error: ' + JSON.stringify(response));
    }
    if (always) {
      always();
    }
  });
}

/* csrf token stuff */
function wire_up_ajax_csrf() {
  /* The whole reason I do this is because backbone.js takes it upon itself to
   * post to the server for you, but they don't include a great way to attach a
   * csrf token. This is also necessary for DELETE requests. Every time you
   * call this it clears out the last one so it's safe to call again. */
  $.ajaxSetup({
    headers: {'X-CSRFToken': get_csrf_token()}
  });
}

function add_csrf_token(data) {
  data['csrfmiddlewaretoken'] = get_csrf_token();
  return data;
}

function get_csrf_token() {
  // In a single-page scenario where the user can log in without reloading the
  // page, the html token can be out of date.
  return get_csrf_token_from_cookie() || get_csrf_token_from_html();
}

function get_csrf_token_from_cookie() {
  var matched = document.cookie.match(/csrftoken=(\w+)/);
  if (matched) {
    return matched[1];
  }
}

function get_csrf_token_from_html() {
  return $('input[name=csrfmiddlewaretoken]').val();
}

function update_field(
    model_name, pk, field_name, new_value, success, always, feedback) {
  var data = {};
  data[field_name] = new_value;
  var url = '{{ api_root_url }}' + model_name + '/' + pk;
  return post(url, data, success, always, feedback);
}

function button_updates_field(
    button, model_name, pk, field_name, new_value, success, always) {
  var feedback = button.parent();
  button.click(function() {
    button.prop('disabled', true);
    var use_always = function() {
      button.prop('disabled', false);
      if (always) {
        always();
      }
    };
    update_field(
        model_name, pk, field_name, new_value, success, use_always, feedback);
  });
}
