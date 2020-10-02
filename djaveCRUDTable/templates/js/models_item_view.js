var ModelsItemView = Backbone.View.extend({
  tagName: 'tr',
  template: _.template(wrapper.find('.list-item-template').html()),

  initialize: function() {
    this.listenTo(this.model, 'change', this.render);
  },

  render: function() {
    var model = this.model;
    var model_data = model.toJSON();
    var id = this.model.get('id');
    if (typeof id == 'undefined') {
      console.log(
          'An API endpoint is returning objects with no id attribute which ' +
          'may cause duplicates in the CRUDTable because you need an id to ' +
          'identify if a row exists already.');
    }
    var row = this.$el.html(this.template(model_data));
    row.attr('data-pk', id);
    inputs(row).each(function() {
      var control = $(this);
      control.val(model.get(control.attr('name')));
    });
    resize_textareas(row);

    var show_edit_mode_buttons_with_save_callback = function(row) {
      show_edit_mode_buttons(row, function() {
        if (options.saved_model_callback) {
          options.saved_model_callback(model.toJSON());
        }
      });
    };
    setup_edit_row_turns_yellow(
        row, show_edit_mode_buttons_with_save_callback, show_original_buttons);

    var view = this;
    var delete_url = view.model.url();
    wire_up_delete_button(view, delete_url, function() {
      view.remove();
      models_view.maybe_hide();
    });

    if (options.modified_row_callback) {
      // There's a race where sometimes row hasn't attached to the dom yet. The
      // modified row callback might want to inspect up the dom tree to find
      // the model.
      var do_or_schedule_modified_row_callback = function() {
        if (row.parent().length) {
          options.modified_row_callback(row, model.toJSON(), model);
        } else {
          window.setTimeout(do_or_schedule_modified_row_callback, 10);
        }
      }
      do_or_schedule_modified_row_callback();
    }

    space_out_buttons(row);  // Keep this last!
    return row;
  }
});
