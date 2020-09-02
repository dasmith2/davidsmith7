var ModelsItemView = Backbone.View.extend({
  tagName: 'tr',
  template: _.template(wrapper.find('.list-item-template').html()),

  initialize: function() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
  },

  events: {
    'click .delete': 'delete'
  },

  delete: function(event) {
    // `destroy` is a Backbone-ism. This simply fires a delete request.
    if (!options.delete_row_confirm_question || confirm(
        options.delete_row_confirm_question)) {
      this.model.destroy();
      if (options.deleted_model_callback) {
        options.deleted_model_callback(this.model);
      }
    }
    event.preventDefault();
  },

  render: function() {
    var model_data = this.model.toJSON();
    var row = this.$el.html(this.template(model_data));
    row.attr('data-pk', this.model.get('id'));
    var model = this.model;
    row.find('input,select,textarea').each(function() {
      var control = $(this);
      control.val(model.get(control.attr('name')));
    });
    row.find('textarea').each(function() {
      resize_textarea($(this));
    });
    if (options.new_row_callback) {
      options.new_row_callback(row, model_data);
    }
    return row;
  }
});
