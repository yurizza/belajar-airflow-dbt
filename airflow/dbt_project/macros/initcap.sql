{% macro initcap(column) %}
    concat(upper(substring({{ column }}, 1, 1)), lower(substring({{ column }}, 2)))
{% endmacro %}
