function post_save_project(project) {
  if (project.has_to_do_list) {
    $('.to_dos_nav').parent().show();
  }
  if (project.use_clock) {
    $('.enter_time_nav').parent().show();
    $('.project_work_summary_nav').parent().show();
  }
  if (project.has_invoices) {
    $('.project_invoices_nav').parent().show();
  }
}

function post_delete_project() {
  $('.archived-projects-link').removeClass('start-hidden').show();
}
