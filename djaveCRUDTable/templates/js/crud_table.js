/* This requires backbone.js and works together with
 * djaveCRUDTable.crud_table.CRUDTable to create a table (with filter_widgets)
 * where each row is an object with an edit and delete button. When you click
 * edit, you're jumped to a panel where you can edit the details. All this
 * happens without page reloads. base_api_url will be something like
 * /api/Project wrapper_finder will be something like '#projects' and
 * save_new_defaults will be something like {} or {'user': 'me'} */

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
      delete_row_confirm_question: null,
      // function new_row_callback(row, model_data) {}
      new_row_callback: null,
      // function saved_model_callback(new_project_data_or_whatever) {}
      saved_model_callback: null,
      // function deleted_model_callback(backbone_model) {}
      deleted_model_callback: null,
      // Should the table display a row up top that allows the user to create
      // new instances?
      inline_create: null};
}

function setup_crud_table(options) {
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
    return options.base_api_url + query();
  }

  function query() {
    var url_parts = {};
    wrapper.find('.filters input').each(function() {
      var filter = $(this);
      var val = filter.val();
      var query_key = filter.attr('data-query-key');
      if (!query_key) {
        console.log('a filter doesnt have a data-query-key');
      } else if (val) {
        url_parts[query_key] = val;
      }
    });
    return query_string_obj_to_str(url_parts);
  }

  function setup_filter_change() {
    wrapper.find('.filter_widgets input').change(function() {
      Backbone.history.navigate(base_url + query(), true);
      reload_list();
    });
  }

  function reload_list() {
    models.reset();
    models.url = api_list_url();
    models.fetch();
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

      function extend_by_save_new_defaults(data) {
        for (const [key, value] of Object.entries(options.save_new_defaults)) {
          data[key] = value;
        }
      }

      {% include "js/models_view.js" %}
      {% include "js/edit_model_view.js" %}

      models_view = new ModelsView({collection: models});
      edit_view = new EditModelView();
      var panel_id = wrapper.find('.details').attr('id');
      on_route(panel_id, function(id) {
        edit_view.edit(id);
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
        callback(model);
        return;
      }
    });
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
}

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
