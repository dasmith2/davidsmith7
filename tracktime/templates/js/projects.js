function post_save_project(project) {
  if (project.has_to_do_list) {
    $('.todo_nav').parent().show();
  }
  if (project.use_clock) {
    $('.clock_nav').parent().show();
    $('.report_nav').parent().show();
  }
  if (project.has_invoices) {
    $('.invoices_nav').parent().show();
  }
}

function post_delete_project() {
  $('.archived-projects-link').removeClass('start-hidden').show();
}
