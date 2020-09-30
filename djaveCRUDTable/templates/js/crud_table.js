/* This requires backbone.js and works together with
 * djaveCRUDTable.crud_table.CRUDTable to create a table (with filter_widgets)
 * where each row is an object with an edit and delete button. When you click
 * edit, you're jumped to a panel where you can edit the details. All this
 * happens without page reloads. base_api_url will be something like
 * /api/Project wrapper_finder will be something like '#projects' and
 * save_new_defaults will be something like {} or {'user': 'me'}
 *
 * djaveCRUDTable/(crud_table.py (def __init__ args and body, as_html),
 * templates/(crud_table.html bottom of the page, js/crud_table.js
 * crud_table_options)) */

function crud_table_options(base_api_url, wrapper_finder) {
  return {
      base_api_url: base_api_url,  // e.g. '/api/Projects'
      wrapper_finder: wrapper_finder,  // e.g. '#project_list_wrapper'
      save_new_defaults: {},  // e.g. {'creator': 'me'}
      // e.g. 'name' as in, "When editing a project with name Foo, label the
      // edit panel like, "Edit Foo"
      label_edit_page_with_field: null,
      // Ask this question before deleting a row. The default question is
      // something like "Delete <model lower case singular name>?"
      confirm_delete_question: null,
      // function modified_row_callback(row, model_data, model) {}
      modified_row_callback: null,
      // function saved_model_callback(new_project_data_or_whatever) {}
      saved_model_callback: null,
      // function deleted_model_callback(backbone_model) {}
      deleted_model_callback: null,
      // Should the table display a row up top that allows the user to create
      // new instances?
      inline_create: null,
      // function inline_create_callback(model_data, create_row) {}
      inline_create_callback: null,
      // function fetch_list_callback(models) {}
      fetch_list_callback: null,
      // Sometimes actions in one panel mean you need to reload a different
      // list. This option allows you to put a function in the global namespace
      // that will reload this list.
      global_reload_function_name: null,
      // function edit_callback(details_panel, model_data) {}
      edit_callback: null,
      // When you have nested lists, you'll probably have to update the
      // save_new_defaults for inner lists. For instance, when you click
      // through to an invoice and want to create a new manual line item, it'll
      // need a dynamic invoice id. But just in case there are other options
      // you'll have to update, I make the entire options object available.
      global_options_variable_name: null};
}

function setup_crud_table(options) {
  if (options.global_options_variable_name) {
    window[options.global_options_variable_name] = options;
  }
  var wrapper = $(options.wrapper_finder);
  var base_url = wrapper.find('.list').attr('data-url');
  if (!base_url) {
    window.onerror(
        'I expect ' + options.wrapper_finder + ' to contain something like '
        + '<div class="list" data-url="/whatever"');
  }

  var Model = Backbone.Model.extend({
    url: function() {
      return options.base_api_url + '/' + this.get('id');
    }
  });

  function api_list_url() {
    return options.base_api_url + api_query();
  }

  function api_query() {
    return query_helper(true);
  }

  function browser_query() {
    return query_helper(false);
  }

  function filters() {
    return wrapper.find('.filters').find('input,select');
  }

  function query_helper(for_api) {
    var url_parts = {};
    filters().each(function() {
      var filter = $(this);
      var val = filter.val();
      var query_key = filter.attr('data-query-key');
      var append_to_val = filter.attr('data-append-to-val');
      var default_val = filter.attr('data-default') || '';
      var changed = filter.attr('type') != 'hidden' && (
          filter.val() != default_val);
      if (append_to_val && for_api) {
        val += append_to_val;
      }
      if (!query_key) {
        console.log('a filter doesnt have a data-query-key');
      } else if ((val && for_api) || (changed && !for_api)) {
        url_parts[query_key] = val;
      }
    });
    return query_string_obj_to_str(url_parts);
  }

  function setup_filter_change() {
    filters().change(function() {
      Backbone.history.navigate(base_url + browser_query(), true);
      reload_list();
    });
  }

  var reload_list = function() {
    models.reset();
    models.url = api_list_url();
    models.fetch();
  }

  if (options.global_reload_function_name) {
    // Now totally unrelated code in completely different files can refresh
    // these models.
    window[options.global_reload_function_name] = reload_list;
  }

  function reload_list_if_qs_sets_filters() {
    /* Returns true iff any values were copied from the query string to the
     * filter_widgets. */
    var any_copied = false;
    var from_qs = get_query_string_obj();
    for (const [key, value] of Object.entries(from_qs)) {
      var on_page = $('[data-query-key=' + key + ']');
      if (on_page.length && on_page.val() != value) {
        any_copied = true;
        on_page.val(value);
      }
    }
    if (any_copied) {
      reload_list();
    }
  }

  var models = null;
  var models_view = null;
  var edit_view = null;
  var initialized = false;
  function init() {
    {% include "js/models_item_view.js" %}

    if (!initialized) {
      initialized = true;
      setup_filter_change();

      var Models = Backbone.Collection.extend({
        model: Model,
        url: api_list_url(),
        parse: function(response) {
          return response.results;
        }
      });
      models = new Models();
      function call_fetch_list_callback_on(event_name) {
        models.on(event_name, function() {
          if (options.fetch_list_callback) {
            options.fetch_list_callback(models.models);
          }
        });
      }
      call_fetch_list_callback_on('sync');
      call_fetch_list_callback_on('destroy');
      call_fetch_list_callback_on('add');

      function extend_by_save_new_defaults(data) {
        for (const [key, value] of Object.entries(options.save_new_defaults)) {
          data[key] = value;
        }
      }

      {% include "js/models_view.js" %}
      {% include "js/edit_model_view.js" %}

      models_view = new ModelsView({collection: models});
      edit_view = new EditModelView();
      var details_panel = wrapper.find('.details');
      on_route(panel_route_name(details_panel), function(id) {
        edit_view.edit(id, function(model_data) {
          if (options.edit_callback) {
            options.edit_callback(details_panel, model_data);
          }
        });
      });
    }
    models.fetch();
  }

  if (typeof current_user == 'undefined') {
    // If current_user does not exist, it's a regular old site where, when you
    // log in, the page reloads. So we can assume it's safe to init.
    init();
  } else {
    // If current_user exists that means the whole site is singe-site and I
    // need to pay attention to current_user in case the user logs in or
    // whatever.
    current_user.on('change', function() {
      if (current_user.get('is_logged_in')) {
        init();
      } else {
        if (models) {
          models.reset();
        }
      }
    });
  }

  function get_model(id, callback) {
    var found = null;
    id = parseInt(id);
    models.each(function(model) {
      if (model.id == id) {
        found = model;
      }
    });
    if (found) {
      callback(found);
      return;
    }
    found = new Model();
    found.url = options.base_api_url;
    if (id) {
      found.url += '/' + id;
      found.fetch({success: function() {
        callback(found);
      }});
    } else {
      callback(found);
    }
  }

  function wire_up_button(button, click) {
    button.off();
    button.click(function(event) {
      event.preventDefault();
      button.prop('disabled', true);
      var always = function() {
        button.prop('disabled', false);
      };
      var feedback = button.parent();
      click(always, feedback);
    });
  }

  function wire_up_delete_button(view, delete_url, success) {
    var delete_button = view.$el.find('.delete');
    wire_up_button(delete_button, function(always, feedback) {
      if (!options.confirm_delete_question || confirm(
          options.confirm_delete_question)) {
        var use_success = function(response) {
          if (success) {
            success(response);
          }
          // DON'T models.fetch() here in order to reload the list because that
          // creates a race.
          window.models = models; // DO NOT SUBMIT
        };
        ajax_delete(delete_url, use_success, always, feedback);
        if (options.deleted_model_callback) {
          options.deleted_model_callback(view.model);
        }
      } else {
        always();
      }
    });
  }

  {% include "js/edit_mode_buttons.js" %}
}

{% include "js/edit_row.js" %}
{% include "js/set_clear_dt_green_mode.js" %}

function str_to_native(my_str) {
  if (my_str === 'null') {
    return null;
  } else if (my_str === 'true') {
    return true;
  } else if (my_str === 'false') {
    return false;
  }
  return my_str;
}

var buttons_cell = function(row) {
  return row.find('.buttons');
};

var other_buttons = function(row) {
  return row.find('button,.button');
};

function find_pk($element) {
  // Search up the dom for a data-pk attribute. So you might do something like
  // my_button.click(function() { var pk = find_pk($(this)); });
  if ($element.attr('data-pk')) {
    return parseInt($element.attr('data-pk'));
  }
  return parseInt($element.parents('[data-pk]').attr('data-pk'));
}

function find_model($element) {
  if ($element.attr('data-model')) {
    return $element.attr('data-model');
  }
  return $element.parents('[data-model]').attr('data-model');
}

function row_by_pk(pk) {
  return $('tr[data-pk=' + pk + ']');
}

function remove_row(pk_or_response) {
  /* It's pretty handy to just have remove_row be the success of button clicks
   * such as Archive. */
  var pk = pk_or_response;
  if (typeof pk_or_response == 'object') {
    pk = pk_or_response['id'];
  }
  var row = row_by_pk(pk);
  var table = row.parents('table');
  row.remove();
  if (!table.find('tbody tr').length) {
    var existing = table.parent().find('.nothing');
    if (existing.length) {
      existing.removeClass('start-hidden').show();
    } else {
      $('<p class="margin-top">Nothing to report</p>').insertAfter(table);
    }
    table.hide();
  }
}

function space_out_buttons(row) {
  var do_space_out = function() {
    var buttons = row.find('button:visible,.button:visible');
    for (var i = 0; i < buttons.length; i++) {
      var button = $(buttons[i]);
      if (i == buttons.length - 1) {
        button.addClass('last-button');
      } else {
        button.removeClass('last-button');
      }
    }
  };

  var all_buttons = row.find('button,.button');
  var buttons = row.find('button:visible,.button:visible');
  if (all_buttons.length && !buttons.length) {
    /* In Firefox I'm getting a race. $('button').show();
     * $('button:visible').length == 0; */
    window.setTimeout(do_space_out, 1);
  } else {
    do_space_out();
  }
}

function val(elt) {
  if (elt.attr('type') == 'checkbox') {
    return elt.is(':checked');
  }
  return elt.val();
}
