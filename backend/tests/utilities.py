def verify_nugget_content_availability(
    instructions, expected_available, expected_conditional, expected_unavailable
):
    # TODO: This is tightly coupled with the instruction prompt which changes frequently
    for content in expected_available:
        assert (
            content in instructions
        ), f"Expected '{content}' to be available in instructions"
        assert (
            content in instructions.split("# Conditionally Available Secrets")[0]
        ), f"Expected '{content}' to be in Available Secrets section"

    for content in expected_conditional:
        assert (
            content in instructions
        ), f"Expected '{content}' to be conditionally available in instructions"
        assert (
            content in instructions.split("# Conditionally Available Secrets")[1]
        ), f"Expected '{content}' to be in Conditionally Available Secrets section"

    for content in expected_unavailable:
        assert (
            content not in instructions
        ), f"Expected '{content}' to be unavailable in instructions"


def assert_contains_any_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = []

    for keyword in keywords:
        if keyword.lower() in text.lower():
            found_keywords.append(keyword)

    assert (
        found_keywords
    ), f"Expected to find at least one keyword from {keywords} in text: {text[:200]}..."
    return found_keywords
