{% if character_memories %}

The following are memories that shape your understanding of the world:
{% for memory in character_memories %}
    - {{ memory.content }}
{% endfor %}
{% endif %}
