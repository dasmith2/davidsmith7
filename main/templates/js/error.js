/* Global error reporter.  */
window.onerror = function(msg, url, line, col, error) {
  url = url || window.location.href;
  var data = {
      msg: msg, url: url, line: line, col: col, stack: error && error.stack}
  $.post('/js_error', data);
};

window.log_error = function(msg) {
  // Don't use, like, throw 'my custom error' because in Firefox at least the
  // message never gets to window.onerror.
  window.onerror(msg);
  console.log(msg);
};
