def find_keywords_in_text(text: str, keywords: list) -> list[str]:
    """Helper function to find keywords in text (case-insensitive)."""
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in text.lower():
            found_keywords.append(keyword)
    return found_keywords


def assert_contains_any_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = find_keywords_in_text(text, keywords)
    assert (
        found_keywords
    ), f"Expected to find at least one keyword from {keywords} in text: {text[:200]}..."
    return found_keywords


def assert_does_not_contain_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = find_keywords_in_text(text, keywords)
    assert (
        not found_keywords
    ), f"Expected to NOT find any keywords from {keywords} in text, but found: {found_keywords}. Text: {text[:200]}..."
    return found_keywords
