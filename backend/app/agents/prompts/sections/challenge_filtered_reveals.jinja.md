{% if filtered_reveals %}

You MUST use the following information in your response if the player asks.
{% for reveal in filtered_reveals %}
    - {{ reveal }}
{% endfor %}
{% endif %}
