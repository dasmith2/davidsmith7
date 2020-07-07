function css(finder, file_name) {
  var this_load_css = function() {
    var actually_load_css = function(old_min_dim) {
      var new_min_dim = Math.min(window.innerWidth, window.innerHeight);
      if (old_min_dim != new_min_dim) {
        return;
      }
      var href = '/css/' + file_name + '?min_dimension=' + new_min_dim;
      var tag = $('.' + finder);
      if (tag.length) {
        tag.attr('href', href);
      } else {
        tag = $('<link rel="stylesheet">').addClass(finder).attr(
          'href', href).appendTo($('head'));
      }
    };

    var old_min_dim = Math.min(window.innerWidth, window.innerHeight);
    if (!$('.' + finder).length) {
      actually_load_css(old_min_dim);
    } else {
      // This is just to avoid reloading the css a bunch of times as the user
      // is resizing the window.
      window.setTimeout(function() {
        actually_load_css(old_min_dim);
      }, 500);
    }
  };

  this_load_css();
  $(window).resize(this_load_css);
}
