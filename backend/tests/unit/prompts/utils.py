import re


def assert_template_rendered_completely(rendered_prompt: str) -> None:
    """Reusable assertion method to check that Jinja template has been fully rendered."""
    assert rendered_prompt is not None

    # Check for any remaining Jinja variable syntax: {{ variable }}
    jinja_variables = re.findall(r"\{\{.*?\}\}", rendered_prompt)
    assert not jinja_variables, f"Found unrendered Jinja variables: {jinja_variables}"

    # Check for any remaining Jinja control structures: {% ... %}
    jinja_controls = re.findall(r"\{%.*?%\}", rendered_prompt)
    assert (
        not jinja_controls
    ), f"Found unrendered Jinja control structures: {jinja_controls}"
