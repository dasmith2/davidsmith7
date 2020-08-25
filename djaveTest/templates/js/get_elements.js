var to_return = [];
$('{{ jquery_selector }}').each(function() {
  to_return.push(this);
});
return to_return;
