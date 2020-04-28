/* Global error reporter */
window.onerror = function(msg, url, line, col, error) {
  url = url || window.location.href;
  $.post('/js_error', {
      msg: msg, url: url, line: line, col: col, stack: error && error.stack});
};
