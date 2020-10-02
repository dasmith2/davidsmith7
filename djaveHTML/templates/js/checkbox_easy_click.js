function checkbox_easy_click(container) {
  container.find('input[type=checkbox]').each(function() {
    var checkbox = $(this);
    checkbox.parent().css('cursor', 'pointer').click(function(event) {
      // https://stackoverflow.com/a/31171219/223268
      if (!$(event.target).is(':checkbox')) {
        checkbox.click();
      }
    });
  });
}
