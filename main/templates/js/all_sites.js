{% include "js/error.js" %}
{% include "js/feedback.js" %}
{{ ajax_js }}
{% include "js/edit.js" %}
{{ edit_list_table_js }}
{% include "js/resize_textareas.js" %}
{% include "js/query_string.js" %}
{% include "js/css.js" %}
{% include "js/px_to_int.js" %}
{% if in_web_test %}
  {% include "js/pause_web_test.js" %}
{% endif %}
