$(function() {
  $('.allfixed').click(function() {
    post('{{ all_fixed_url }}', {}, function() {
      location.reload();
    });
  });
});
