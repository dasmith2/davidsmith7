var ModelsView = Backbone.View.extend({
  el: wrapper.find('.list-table-wrapper'),
  initialize: function() {
    this.listenTo(this.collection, 'add', this.add_one);
    this.listenTo(this.collection, 'reset', this.remove_all);
    this.listenTo(this.collection, 'all', this.log_event);
    this.listenTo(this.collection, 'remove', this.remove_one);
    this.listenTo(this.collection, 'sync', this.maybe_hide);
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
    var create_row = this.$el.find('.inline-create-row');
    var buttons_wrapper = create_row.find('.buttons');
    var me = this;
    var success = function(response_data) {
      var _inputs = me.create_row_inputs();
      _inputs.each(function() {
        if (this.tagName != 'SELECT') {
          $(this).val('');
        }
      });
      set_saved_values(_inputs);
      calc_edit_mode(create_row);
      resize_textareas(create_row);

      me.collection.add(response_data);
      if (options.inline_create_callback) {
        options.inline_create_callback(response_data, create_row);
      }
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
    return inputs(this.$el.find('.inline-create-row'));
  },
  extend_by_create_row: function(data) {
    this.create_row_inputs().each(function() {
      var elt = $(this);
      data[elt.attr('name')] = elt.val();
    });
  },
  setup_inline_create: function() {
    this.table().removeClass('start-hidden');
    var create_row = this.table().find('.inline-create-row');
    setup_edit_row_turns_yellow(create_row);
    resize_textareas(create_row);
  },
  add_one: function(model) {
    this.table().show();
    this.$el.find('.nothing').hide();
    var view = new ModelsItemView({model: model});
    var row = view.render()
    this.tbody().prepend(row);
    var in_table_button_wrapper = this.$el.find(
        '.in-table-button-wrapper');
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
  remove_one: function(model) {
    this.tbody().find(`tr[data-pk=${model.get('id')}]`).remove();
    this.maybe_hide();
  },
  maybe_hide: function() {
    if (!this.tbody().find('tr').length && !options.inline_create) {
      this.show_nothing();
    }
  },
  show_nothing: function() {
    if (!this.$el.find('.inline-create-row').length) {
      this.table().hide();
      var can_create_new = this.$el.find('.createnew').length;
      if (can_create_new) {
        wrapper.find('.upper-new-button-wrapper').removeClass(
            'start-hidden').show();
      } else {
        this.$el.find('.nothing').removeClass('start-hidden').show();
      }
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
