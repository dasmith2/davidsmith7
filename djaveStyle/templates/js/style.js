var on_displayed_callbacks = [];
var displayed_already = false;

function on_display(callback) {
  /* Like $(...) except it runs once all_sites.css loads which causes
   * everything on the page to become visible. */
  if (displayed_already) {
    callback();
  } else {
    on_displayed_callbacks.push(callback);
  }
}

function css(finder, file_name) {
  /* I used to $(window).resize(...). But that turned out to be outsmarting
   * myself. When you click into a text box on mobile, the keyboard pops up,
   * and changes the size of the screen. */

  var on_load = function() {};
  if (file_name == 'all_sites.css') {
    // The page starts hidden and all_sites.css shows the page. But that breaks
    // autofocus because an element can only focus once it's shown.
    on_load = function() {
      displayed_already = true;
      $('[autofocus]').focus();
      for (var i = 0; i < on_displayed_callbacks.length; i++) {
        on_displayed_callbacks[i]();
      }
    };
  }
  var href = '/css/' + file_name + '?zoom=' + automatic_zoom_factor();
  var link = $('<link rel="stylesheet" type="text/css"/>').attr(
      'href', href).appendTo($('head'));
  // jQuery raises an obfuscated error if I link.load(on_load)
  link[0].onload = on_load;
}

function automatic_zoom_factor() {
  /* My desktop has screen size 860 and looks best with zoom factor 0.9 My
   * phone has screen size 360 and looks best with zoom factor 0.64 So 860 * a
   * + b = 0.9 and 360 * a + b = 0.64, solve for a and b. */
  var full_value = (min_screen_dimension()  + 871) / 1923;
  return Math.round(100 * full_value) / 100;
}

function min_screen_dimension() {
  return Math.min(window.innerWidth, window.innerHeight);
}
