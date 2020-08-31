/* This requires backbone.js and works together with
 * djaveCRUDTable.crud_table.CRUDTable to create a table (with filter_widgets)
 * where each row is an object with an edit and delete button. When you click
 * edit, you're jumped to a panel where you can edit the details. All this
 * happens without page reloads. base_api_url will be something like
 * /api/Project wrapper_finder will be something like '#projects' and
 * save_new_defaults will be something like {} or {'user': 'me'} */
function setup_crud_table(
    base_api_url, wrapper_finder, save_new_defaults,
    label_edit_page_with_field, delete_row_confirm_question) {
  var wrapper = $(wrapper_finder);
  var base_url = wrapper.find('.list').attr('data-url');
  if (!base_url) {
    window.onerror(
        'I expect ' + wrapper_finder + ' to contain something like '
        + '<div class="list" data-url="/whatever"');
  }

  var Model = Backbone.Model.extend({
    url: function() {
      return base_api_url + '/' + this.get('id');
    }
  });

  function api_list_url() {
    return base_api_url + query();
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
    var ModelsItemView = Backbone.View.extend({
      tagName: 'tr',
      template: _.template(wrapper.find('.list-item-template').html()),

      initialize: function() {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
        var view = this;
      },

      events: {
        'click .delete': 'delete'
      },

      delete: function(event) {
        // `destroy` is a Backbone-ism. This simply fires a delete request.
        if (!delete_row_confirm_question || confirm(
            delete_row_confirm_question)) {
          this.model.destroy();
        }
        event.preventDefault();
      },

      render: function() {
        return this.$el.html(this.template(this.model.toJSON()));
      }
    });

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

      var ModelsView = Backbone.View.extend({
        el: wrapper.find('.list-table-wrapper'),
        initialize: function() {
          this.listenTo(this.collection, 'add', this.add_one);
          this.listenTo(this.collection, 'reset', this.remove_all);
          this.listenTo(this.collection, 'all', this.log_event);
          this.listenTo(this.collection, 'remove', this.maybe_hide);
          reload_list_if_qs_sets_filters();
        },
        add_one: function(model) {
          this.table().show();
          this.$el.find('.nothing').hide();
          var view = new ModelsItemView({model: model});
          this.tbody().append(view.render());
          var in_table_button_wrapper = this.$el.find(
              '.in-table-new-button-wrapper');
          if (in_table_button_wrapper.length) {
            in_table_button_wrapper.show();
            wrapper.find('.upper-new-button-wrapper').hide();
          }
          this.color_alternate_rows();
        },
        color_alternate_rows: function() {
          window.thisel = this.$el;
          this.$el.find('tbody tr').each(function(i) {
            if (i % 2 == 0) {
              $(this).removeClass('row2');
            } else {
              $(this).addClass('row2');
            }
          });
        },
        remove_all: function() {
          this.tbody().empty();
          this.show_nothing();
        },
        maybe_hide: function() {
          if (!this.tbody().find('tr').length) {
            this.show_nothing();
          }
        },
        show_nothing: function() {
          this.table().hide();
          // If there are no filter_widgets and no rows, then the only thing
          // worth showing is the create new button.
          if (this.$el.find('.filter_widgets').length) {
            this.$el.find('.nothing').show();
          } else {
            wrapper.find('.upper-new-button-wrapper').show();
          }
        },
        log_event: function(action) {
          // console.log(action); // Not sure what events are happening when?
        },
        table: function() {
          return wrapper.find('.list-table');
        },
        tbody: function() {
          return this.table().find('tbody');
        }
      });

      var EditModelView = Backbone.View.extend({
        el: wrapper.find('.details'),
        initialize: function() {
          var view = this;
          if (view.$el.is(':visible')) {
            var id = parseInt(location.pathname.split('/')[2]);
            view.edit(id);
          }

          var save_button = view.$el.find('.save').off();
          save_button.click(function(event) {
            event.preventDefault();
            save_button.prop('disabled', true);
            var always = function() {
              save_button.prop('disabled', false);
            };

            var data = {};
            if (!view.model.get('id')) {  // The id is undefined for new
              for (const [key, value] of Object.entries(save_new_defaults)) {
                data[key] = value;
              }
            }
            view.$el.find('table').find('input,textarea').each(function() {
              var field = $(this);
              var field_name = field.attr('class');
              var value = field.val();
              if (field.attr('type') == 'checkbox') {
                value = field[0].checked;
              }
              data[field_name] = value;
            });

            var feedback = view.$el.find('.feedback');
            var success = function() {
              // I used to think, hey, update the model right on the page and
              // you don't even have to fetch the list. But the user could
              // easily update a field that causes the item to move around in
              // the list, leave entirely, whatever. Let's not outsmart myself
              // here.
              models.fetch();
              var list_panel_id = wrapper.find('.list').attr('id');
              navigate_to_panel(list_panel_id);
            };
            post(view.url, data, success, always, feedback)
          });
        },
        edit: function(id) {
          // Resets the whole row turns yellow on edit thing.
          set_saved_values(this.$el.find('input,textarea'));
          this.$el.find('.edit-table tr').each(function() {
            calc_edit_mode($(this));
          });

          var id_int = parseInt(id);
          var view = this;
          var got_model_callback = function(model) {
            view.model = model;
            view.url = base_api_url;
            if (id_int > 0) {
              view.url += '/' + id_int;
            }

            var model = view.model;
            var lower_case_singular = wrapper.find('.details').attr('id');
            var title = 'New ' + lower_case_singular;
            if (model.get('id') > 0) {
              what_to_call_it = lower_case_singular;
              if (label_edit_page_with_field) {
                what_to_call_it = model.get(label_edit_page_with_field);
              }
              title = 'Edit ' + what_to_call_it;
            }
            view.$el.find('h1').text(title);
            view.$el.find('table').find('input,textarea').each(function() {
              var field = $(this);
              var field_name = field.attr('class');
              var value = model.get(field_name);
              if (field.attr('type') == 'checkbox') {
                field[0].checked = value;
              } else {
                field.val(value);
                if (field[0].tagName == 'TEXTAREA') {
                  resize_textarea(field);
                }
              }
            });
          };
          get_model(id_int, got_model_callback);
        }
      });

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
    found.url = base_api_url;
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
