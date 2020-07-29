{% include "js/error.js" %}
{% include "js/feedback.js" %}
{{ ajax_js }}
{% include "js/edit.js" %}
{{ edit_list_table_js }}
{% include "js/query_string.js" %}
{% include "js/style.js" %}
{% if in_web_test %}
  {% include "js/pause_web_test.js" %}
{% endif %}
