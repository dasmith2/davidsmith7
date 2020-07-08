function css(finder, file_name) {
  /* I used to $(window).resize(...). But that turned out to be outsmarting
   * myself. When you click into a text box on mobile, the keyboard pops up,
   * and changes the size of the screen. */
  var href = '/css/' + file_name + '?zoom=' + automatic_zoom_factor();
  $('<link rel="stylesheet">').attr('href', href).appendTo($('head'));
}

function automatic_zoom_factor() {
  var min_dim = Math.min(window.innerWidth, window.innerHeight);
  var full_value = min_dim / 600.0;
  return Math.round(full_value * 100) / 100;
}
