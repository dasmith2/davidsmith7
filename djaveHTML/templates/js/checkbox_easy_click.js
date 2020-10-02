function checkbox_easy_click(container) {
  container.find('input[type=checkbox]').each(function() {
    var checkbox = $(this);
    checkbox.parent().css('cursor', 'pointer').click(function() {
      checkbox.prop('checked', !checkbox.prop('checked'));
    });
  });
}
