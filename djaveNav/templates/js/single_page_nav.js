/* Single page app nav stuff. This is about creating the ability to navigate to
 * a new url, show the corresponding panels, but not reload the page. */

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

function route_url_from_data_url(data_url) {
  if (data_url.length && data_url.substring(0, 1) == '/') {
    // Typically the case because data-url='/projects' makes more sense
    // than data-url='projects' but Backbone.js requires no leading /
    return data_url.substring(1, data_url.length);
  }
  return data_url;
}

function panel_route_name(panel_or_panel_id) {
  var panel = panel_or_panel_id;
  if (typeof panel_or_panel_id == 'string') {
    panel = $('#' + panel_or_panel_id);
  }
  return route_name_from_url(panel.attr('data-url'));
}

function route_name_from_url(data_url) {
  var route_url = route_url_from_data_url(data_url);
  return route_url.replace(/:\w+/g, '_param').replace(/[^\w]/g, '');
}

$(function() {
  if (!$('.panel').length) {
    // For instance, /errors doesn't have single page navigation.
    return;
  }

  var router_routes_etc = function() {
    // In Backbone.js land, routes are key value pairs where the key is a url
    // pattern like invoices/:pk or whatever, and the value is the NAME of the
    // function on the router that should get called when the browser URL
    // matches that pattern. I guess Backbone.js doesn't do routes[route_url] =
    // route_function because multiple route_urls can point to the same
    // function, and whoever built Backbone.js didn't know about function
    // pointers? I don't know.
    var routes = {};
    var extend_router_by = {
      routes: routes
    };
    $('.panel').each(function() {
      var panel = $(this);
      // Every panel describes what url should make it appear. Multiple panels
      // may share the same data-url. If your panel isn't showing up, this is a
      // likely culprit: the panel's data-url doesn't match the browser url.
      var data_url = panel.attr('data-url');
      var route_url = route_url_from_data_url(data_url);
      var route_name = panel_route_name(panel);
      panel.attr('data-route-name', route_name);
      routes[route_url] = route_name;
      extend_router_by[route_name] = function() {
        $('.panel').each(function() {
          var panel = $(this);
          if (panel_route_name(panel) == route_name) {
            panel.removeClass('start-hidden').show();
          } else {
            panel.hide();
          }
        });
      };
    });
    // At this point, extend_router_by probably looks something like
    // {'projectspk': function() { $('.panel[data-url="/projects/:pk"]').show()
    // }, routes: {'projects/:pk': 'projectspk'}}
    return extend_router_by;
  };

  var init_router = function() {
    var Router = Backbone.Router.extend(router_routes_etc());
    router = new Router();

    for (var i = 0; i < router_exists_callbacks.length; i++) {
      router_exists_callbacks[i]();
    }

    var highlight_nav = function(route_function_name) {
      this.current = route_function_name;
      $('.panel[data-route-name="' + route_function_name + '"]').each(function() {
        var panel = $(this);
        var data_url = panel.attr('data-url');
        var data_nav_css_class = panel.attr('data-nav-css-class');
        $('.nav div').removeClass('current');
        $('.nav_item').each(function() {
          var a = $(this);
          var wrapper = $(a.parents('div')[0]);
          if (data_nav_css_class) {
            if (a.hasClass(data_nav_css_class)) {
              wrapper.addClass('current');
            }
          } else if (data_url.indexOf(a.attr('href')) == 0) {
            // data_url might be "/trips/:pk" and the nav might be to "/trips"
            wrapper.addClass('current');
          }
        });
      });
    };

    router.on('route', highlight_nav);
    return router;
  };

  window.router = init_router();

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
