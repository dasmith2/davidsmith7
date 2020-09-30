function hide_project_column() {
  var existing = $('#hide_project_column');
  if (!existing.length) {
    var style = '.project_name,td.project { display: none; }';
    $(`<style id="hide_project_column">${style}</style>`).appendTo($('body'));
  }
}

function show_project_column() {
  $('#hide_project_column').remove();
}

function set_project_column_visibility() {
  var project_id_finder = window.location.search.match(/project=(\d+)/);
  if (project_id_finder) {
    var specific_project_id = parseInt(project_id_finder[1]);
    // We're about to hide the project select in the create new row, so we have
    // to set it to the correct value from the query string.
    $('.inline-create-row select[name=project]').val(specific_project_id);
    hide_project_column();
  } else {
    show_project_column();
  }
}

on_display(function() {
  set_project_column_visibility();
  router.on('route', function() {
    set_project_column_visibility();
  });
});
