def assert_contains_any_keywords(text: str, keywords: list) -> list[str]:
    found_keywords = []

    for keyword in keywords:
        if keyword.lower() in text.lower():
            found_keywords.append(keyword)

    assert (
        found_keywords
    ), f"Expected to find at least one keyword from {keywords} in text: {text[:200]}..."
    return found_keywords
