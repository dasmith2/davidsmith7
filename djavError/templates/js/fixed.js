on_display(function() {
  $('.list-table thead .allfixed').click(function() {
    var table = $(this).parents('.list-table');
    table.find('button.fixed').click();
  });
});

function modified_fixable_row_callback(row, model_data, model) {
  on_display(function() {
    var model_name = find_model(row);
    var pk = find_pk(row);

    var fixed_button = row.find('button.fixed');
    var not_fixed_button = row.find('button.notfixed');
    button_updates_field(fixed_button, model_name, pk, 'fixed', 'now', function() {
      model.set({fixed: 'now', fixed_str: 'Now'});
    });
    button_updates_field(
        not_fixed_button, model_name, pk, 'fixed', null, function() {
      model.set({fixed: null, fixed_str: ''});
    });
    if (model_data.fixed) {
      row.addClass('green');
      fixed_button.hide();
      not_fixed_button.removeClass('start-hidden').show();
    } else {
      fixed_button.show();
      not_fixed_button.hide();
      row.removeClass('green');
    }
  });
}
