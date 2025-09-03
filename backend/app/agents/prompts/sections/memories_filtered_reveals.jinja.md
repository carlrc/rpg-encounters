Use the following memories{% if filtered_reveals %} and reveals{% endif %} in your responses.
{% include 'memories.jinja.md' %}
{% if filtered_reveals %}
{% include 'challenge_filtered_reveals.jinja.md' %}
{% endif %}
