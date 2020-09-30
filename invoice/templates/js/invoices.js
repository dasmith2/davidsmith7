function modified_invoice_row_callback(row, model_data, model) {
  var buttons = row.find('.buttons');

  var view_button = buttons.find('a.view');
  if (!view_button.length) {
    var view_url = '{{ view_invoice_url_base }}' + model_data.id;
    view_button = $('<a class="button view"></a>').attr(
        'href', view_url).appendTo(buttons);
  }

  var paid_button_helper = function(css_class, button_text, new_paid_value) {
    var button = buttons.find('.' + css_class);
    if (!button.length) {
      button = $('<button></button>').addClass(css_class).text(
          button_text).appendTo(buttons);
      var success = function(data) {
        model.set({  // This triggers a re-render.
            'paid': data.paid, 'status_with_date': data.status_with_date});
      };
      button_updates_field(
          button, 'Invoice', model_data.id, 'paid', new_paid_value, success);
    }
    return button;
  };
  var paid_button = paid_button_helper('paid', 'Paid', 'now');
  var not_paid_button = paid_button_helper('not_paid', 'Not paid', null);

  var edit_button = buttons.find('.edit');

  if (model_data.paid) {
    paid_button.hide();
    edit_button.hide();
    not_paid_button.show();
    view_button.text('View');
    row.addClass('green').removeClass('yellow');
  } else if (model_data.sent) {
    paid_button.show();
    edit_button.show();
    not_paid_button.hide();
    view_button.text('Preview');
    row.addClass('yellow').removeClass('green');
  } else {
    paid_button.hide();
    edit_button.show();
    not_paid_button.hide();
    view_button.text('Preview');
    row.removeClass('yellow').removeClass('green');
  }
  space_out_buttons(row);
}

function edit_invoice_callback(details_panel, invoice_data) {
  var filters = $('#lineitems-wrapper .filters');
  var filter = filters.find('.invoice');
  if (!filter.length) {
    filter = $(
        '<input class="invoice" type="hidden" name="invoice" ' +
        'data-query-key="invoice">').appendTo(filters);
  }
  filter.val(invoice_data.id);
  // reload_line_items was placed in the global namespace by the
  // global_reload_function_name option.
  reload_line_items();
  // line_items_options was placed in the global namespace by the
  // global_options_variable_name option.
  line_items_options.save_new_defaults['invoice'] = invoice_data.id;

  window.details_panel = details_panel; // DO NOT SUBMIT
  window.invoice_data = invoice_data; // DO NOT SUBMIT
  var view_button = details_panel.find('a.view');
  if (!view_button.length) {
    view_button = $('<a class="view button">View</a>').appendTo(
        buttons_cell(details_panel));
  }
  view_button.attr('href', invoice_data.view_url);
}
