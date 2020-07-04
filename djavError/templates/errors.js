function init_fixed_mode() {
  var table_finder = 'table[data-model="Error"]';
  var field_name = 'fixed';
  setup_set_clear_dt_green_mode(table_finder, field_name, 'Fix', 'Unfix');
}

$(init_fixed_mode);
