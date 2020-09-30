function new_project_invoice_rule_row_callback(row, model_data) {
  var button_html =
      '<button class="createnewinvoice">Create new invoice</button>';
  var data = {'project_invoice_rule_id': find_pk(row)};
  var create_button = $(button_html);
  var success = function() {
    // reload_invoices was placed in the global namespace by the
    // global_reload_function_name option.
    reload_invoices();
  };
  var always = function() {
    create_button.prop('disabled', false);
  };
  var cell = buttons_cell(row);
  create_button.click(function() {
    create_button.prop('disabled', true);
    post('{{ create_invoice_url }}', data, success, always, cell);
  });
  cell.append(create_button);
}

function edit_project_invoice_rule_callback(details_panel, model_data) {
  var h = 'New invoice rule';
  if (model_data['id']) {
    h = 'Edit ' + model_data.project_name + ' invoice rule';
  }
  details_panel.find('h1').text(h);
}
