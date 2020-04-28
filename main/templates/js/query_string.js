/* Query string stuff */
function query_string_obj_to_str(obj) {
  var parts = [];
  for (var key in obj) {
    if (obj[key]) {
      if (Array.isArray(obj[key])) {
        for (var i = 0; i < obj[key].length; i++) {
          parts.push(key + '=' + obj[key][i]);
        }
      } else {
        parts.push(key + '=' + obj[key]);
      }
    }
  }
  if (parts.length) {
    return '?' + parts.join('&');
  }
  return '';
}

function get_query_string_obj(search) {
  if (typeof(search) == 'undefined') {
    search = window.location.search;
  }
  var obj = {};
  if (search) {
    if (search.substring(0, 1) == "?") {
      search = search.substring(1);
    }
    search.split('&').forEach(function(part) {
        if (Boolean(part)) {
          var sub_parts = part.split('=');
          if (sub_parts.length == 2) {
            obj[sub_parts[0]] = sub_parts[1];
          }
        }
      });
  }
  return obj;
}

function refresh_with_qs(key, value) {
  // Go to the exact same URL we're on with one difference: the query string
  // key=value. Or, if value is null, with that query string variable not set.
  var search_obj = get_query_string_obj();
  if (typeof(value) == 'undefined' || value === null) {
    if (key in search_obj) {
      delete search_obj[key];
    }
  } else {
    search_obj[key] = value;
  }
  window.location = (
      window.location.pathname + query_string_obj_to_str(search_obj));
}
