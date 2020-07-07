function css(finder, file_name) {
  /* I used to $(window).resize(...). But that turned out to be outsmarting
   * myself. When you click into a text box on mobile, the keyboard pops up,
   * and changes the size of the screen. */
  var min_dim = Math.min(window.innerWidth, window.innerHeight);
  var href = '/css/' + file_name + '?min_dimension=' + min_dim;
  $('<link rel="stylesheet">').attr('href', href).appendTo($('head'));
}
