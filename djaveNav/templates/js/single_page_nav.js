/* Single page app nav stuff. This is about creating the ability to navigate to
 * a new url, show the corresponding panel, but not reload the page. */

// Public stuff
var router = null;  // So you can router.on("route:help", function(page) {

function navigate_to_panel(panel_name) {
  var panel = $('#' + panel_name);
  Backbone.history.navigate(panel.attr('data-url'), true);
}

var on_display = function(callback) {
  /* Wait until all the navigation stuff is wired up before calling the
   * callback. */
  if (nav_is_ready) {
    callback();
  } else {
    on_display_callbacks.push(callback);
  }
};

function on_route(panel_id, callback) {
  var do_on_route = function() {
    router.on('route:' + panel_id, callback);
  };
  if (router) {
    do_on_route();
  } else {
    router_exists_callbacks.push(do_on_route);
  }
}

// Private stuff
var single_page_panel = null;
var nav_is_ready = false;
var on_display_callbacks = [];
var router_exists_callbacks = [];

$(function() {
  if (!$('.panel').length) {
    // For instance, /errors doesn't have single page navigation.
    return;
  }
  var find_panel_routes = function() {
    var panel_routes = {};
    $('.panel').each(function() {
      var url = $(this).attr('data-url');
      var name = $(this).attr('id');
      var route_url = url;
      if (route_url.length && route_url.substring(0, 1) == '/') {
        route_url = route_url.substring(1, route_url.length);
      }
      panel_routes[route_url] = name;
    });
    return panel_routes;
  };

  var show_panel = function(panel_name) {
    $('.panel').each(function() {
      var panel = $(this);
      if (panel_name == panel.attr('id')) {
        single_page_panel = panel;
        panel.show();
      } else {
        panel.hide();
      }
    });
  };

  var get_extend_router_by = function() {
    var extend_router_by = {
      routes: find_panel_routes()
    };
    $('.panel').each(function() {
      var panel_name = $(this).attr('id');
      extend_router_by[panel_name] = function() {
        show_panel(panel_name);
      };
    });
    return extend_router_by;
  };

  var init_router = function() {
    var Router = Backbone.Router.extend(get_extend_router_by());
    router = new Router();

    for (var i = 0; i < router_exists_callbacks.length; i++) {
      router_exists_callbacks[i]();
    }

    router.on('route', function(panel_id) {
      this.current = panel_id;
      var set_current_nav_item = function(current_panel_id) {
        var data_url = $('#' + current_panel_id).attr('data-url');
        $('.nav_item').each(function() {
          var a = $(this);
          var wrapper = $(a.parents('div')[0]);
          // data_url might be "/trips/:pk" and the nav might be to "/trips"
          if (data_url.indexOf(a.attr('href')) == 0) {
            wrapper.addClass('current');
          } else {
            wrapper.removeClass('current');
          }
        });
      };

      set_current_nav_item(panel_id);
    });
  };

  init_router();

  Backbone.history.start({pushState: true});

  var setup_nav_clicks = function() {
    $(document).on('click', 'a[href]', function(evt) {
      var a_href = $(this).attr('href');
      $('.panel').each(function() {
        if (url_matches_panel(a_href, $(this).attr('data-url'))) {
          evt.preventDefault();
          Backbone.history.navigate(a_href, true);
        }
      });
    });
  }
  setup_nav_clicks();
  nav_is_ready = true;
  for (var i = 0; i < on_display_callbacks.length; i++) {
    on_display_callbacks[i]();
  }
});

var url_matches_panel = function(url, panel_url) {
  /* Does the given url point to the given panel?  url_matches_panel('/w',
   * '/w') => true, url_matches_panel('/w/2', '/w') => false,
   * url_matches_panel('/w/2', '/w/:x') => true */
  var url_parts = url.split('/')
  var panel_parts = panel_url.split('/');
  if (url_parts.length != panel_parts.length) {
    return false;
  }

  var parts_match = function(url_part, panel_part) {
    var is_variable = panel_part.substring(0, 1) == ':';
    return (is_variable && url_part.length) || (url_part == panel_part);
  };

  for (var i = 0; i < url_parts.length; i++) {
    if (!parts_match(url_parts[i], panel_parts[i])) {
      return false;
    }
  }
  return true;
};
