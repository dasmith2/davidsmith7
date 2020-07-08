function css(finder, file_name) {
  /* I used to $(window).resize(...). But that turned out to be outsmarting
   * myself. When you click into a text box on mobile, the keyboard pops up,
   * and changes the size of the screen. */
  var href = '/css/' + file_name + '?zoom=' + automatic_zoom_factor();
  $('<link rel="stylesheet">').attr('href', href).appendTo($('head'));
}

function automatic_zoom_factor() {
  /* My desktop has screen size 860 and looks best with zoom factor 1.0 My
   * phone has screen size 360 and looks best with zoom factor 0.6 */
  var full_value = (min_screen_dimension()  + 577) / 1562;
  return Math.round(100 * full_value) / 100;
}

function min_screen_dimension() {
  return Math.min(window.innerWidth, window.innerHeight);
}
