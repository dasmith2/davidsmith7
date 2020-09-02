var ModelsView = Backbone.View.extend({
  el: wrapper.find('.list-table-wrapper'),
  initialize: function() {
    this.listenTo(this.collection, 'add', this.add_one);
    this.listenTo(this.collection, 'reset', this.remove_all);
    this.listenTo(this.collection, 'all', this.log_event);
    this.listenTo(this.collection, 'remove', this.maybe_hide);
    reload_list_if_qs_sets_filters();
    if (options.inline_create) {
      this.setup_inline_create();
    }
  },
  events: {
    'click .inline-create-row button': 'create'
  },
  create: function(event) {
    var button = event.target;
    var create_data = {};
    this.extend_by_button_attrs(create_data, button);
    this.extend_by_create_row(create_data);
    extend_by_save_new_defaults(create_data);
    var buttons_wrapper = this.$el.find('.inline-create-row .buttons');
    var inputs = this.create_row_inputs();
    var me = this;
    var success = function(response_data) {
      inputs.each(function() {
        $(this).val('');
      });
      me.collection.add(response_data);
    };
    buttons_wrapper.find('button').prop('disabled', true);
    var always = function() {
      buttons_wrapper.find('button').prop('disabled', false);
    };
    var feedback = buttons_wrapper;
    post(options.base_api_url, create_data, success, always, feedback);
  },
  extend_by_button_attrs: function(data, button) {
    for (var i = 0; i < button.attributes.length; i++) {
      var attr = button.attributes[i];
      var name = attr.name;
      var value = str_to_native(attr.value);
      if (name.indexOf('data-') === 0) {
        data[name.slice('data-'.length)] = value;
      }
    }
  },
  create_row_inputs: function() {
    return this.$el.find('.inline-create-row').find(
        'textarea,select,input');
  },
  extend_by_create_row: function(data) {
    this.create_row_inputs().each(function() {
      var elt = $(this);
      data[elt.attr('name')] = elt.val();
    });
  },
  setup_inline_create: function() {
    this.table().removeClass('start-hidden');
  },
  add_one: function(model) {
    this.table().show();
    this.$el.find('.nothing').hide();
    var view = new ModelsItemView({model: model});
    var row = view.render()
    this.tbody().prepend(row);
    var in_table_button_wrapper = this.$el.find(
        '.in-table-new-button-wrapper');
    if (in_table_button_wrapper.length) {
      in_table_button_wrapper.show();
      wrapper.find('.upper-new-button-wrapper').hide();
    }
    this.color_alternate_rows();
  },
  color_alternate_rows: function() {
    // If there's a create new row, that'll be white, so the first model
    // row should be grey. But if there isn't a create new row, the first
    // model row will be the first row, so it should be white.
    var row2_on = this.$el.find('.inline-create-row').length ? 1 : 0;
    this.$el.find('tbody tr').each(function(i) {
      if (i % 2 == row2_on) {
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
    if (!this.tbody().find('tr').length && !options.inline_create) {
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
