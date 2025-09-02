# Instructions

Use the following memories{% if filtered_reveals %} and reveals{% endif %} in your responses.
{% include 'sections/character_memories.jinja.md' %}
{% if filtered_reveals %}
{% include 'sections/challenge_filtered_reveals.jinja.md' %}
{% endif %}
