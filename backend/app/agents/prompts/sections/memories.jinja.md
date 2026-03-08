{% if memories is defined and memories %}

The following are memories that shape your understanding of the world:
{% for memory in memories %}
    - {{ memory.content }}
{% endfor %}
{% else %}
IMPORTANT: No memories available for this character. Base your responses on reveals and/or character background only.
{% endif %}
