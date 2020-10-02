var EditModelView = Backbone.View.extend({
  el: wrapper.find('.details'),

  refresh_and_return_to_list: function() {
    models.fetch();
    var list_panel_id = wrapper.find('.list').attr('id');
    navigate_to_panel(list_panel_id);
  },

  initialize: function() {
    var view = this;
    if (view.$el.is(':visible')) {
      var id = parseInt(location.pathname.split('/')[2]);
      view.edit(id);
    }
    checkbox_easy_click(view.$el);

    var save_button = view.$el.find('.save');
    wire_up_button(save_button, function(always, feedback) {
      var data = {};
      if (!view.model.get('id')) {  // The id is undefined for new
        extend_by_save_new_defaults(data);
      }
      view.$el.find('table').find('input,textarea,select').each(function() {
        var field = $(this);
        var field_name = field.attr('name');
        var value = field.val();
        if (field.attr('type') == 'checkbox') {
          value = field[0].checked;
        }
        data[field_name] = value;
      });

      var success = function(success_data) {
        // I used to think, hey, update the model right on the page and you
        // don't even have to fetch the list. But the user could easily update
        // a field that causes the item to move around in the list, leave
        // entirely, whatever. Let's not outsmart myself here.
        if (options.saved_model_callback) {
          options.saved_model_callback(success_data);
        }
        view.refresh_and_return_to_list();
      };
      post(view.url, data, success, always, feedback);
    });
  },
  edit: function(id, edit_callback) {
    // Resets the whole row turns yellow on edit thing.
    set_saved_values(this.$el.find('input,textarea'));
    this.$el.find('.edit-table tr').each(function() {
      calc_edit_mode($(this));
    });

    var id_int = parseInt(id);
    var view = this;
    var got_model_callback = function(model) {
      var table = view.$el.find('table');

      view.model = model;
      view.url = options.base_api_url;
      if (id_int > 0) {
        view.url += '/' + id_int;
      }

      var delete_button = table.find('.delete');
      if (!model.get('id')) {
        delete_button.hide();
      } else {
        delete_button.show();
        wire_up_delete_button(view, view.url, function() {
          view.refresh_and_return_to_list();
        });
      }

      var lower_case_singular = wrapper.find('.details').attr('id');
      var title = 'New ' + lower_case_singular;
      if (model.get('id') > 0) {
        what_to_call_it = lower_case_singular;
        if (options.label_edit_page_with_field) {
          what_to_call_it = model.get(options.label_edit_page_with_field);
        }
        title = 'Edit ' + what_to_call_it;
      }
      view.$el.find('h1').text(title);

      table.find('input,textarea').each(function() {
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
      table.find('.readonly').each(function() {
        var cell = $(this);
        cell.html(model.get(cell.attr('data-field')));
      });

      if (edit_callback) {
        edit_callback(model.toJSON());
      }
    };
    get_model(id_int, got_model_callback);
  }
});
