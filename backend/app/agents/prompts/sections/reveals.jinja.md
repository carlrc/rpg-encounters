{% if reveals is defined and reveals %}

Reference these reveals in your response:
{% for reveal in reveals %}
    **REVEAL ID {{ reveal.id }}: {{ reveal.title }}**:
        - STANDARD: {{ reveal.level_1_content }}
        {% if reveal.level_2_content %}
        - PRIVILEGED: {{ reveal.level_2_content }}
        {% endif %}
        {% if reveal.level_3_content %}
        - EXCLUSIVE: {{ reveal.level_3_content }}
        {% endif %}
{% endfor %}
{% else %}
IMPORTANT: No reveals available for this character. Base your responses on memories and/or character background only.
{% endif %}
