function put_sum_hours_in_header(models) {
  var total = 0.0;
  for (var i = 0; i < models.length; i++) {
    total += models[i].get('hours');
  }
  var new_header = 'Hours'
  if (total > 0) {
    new_header += ': ' + total;
  }
  $('.hours_header').text(new_header);
}
