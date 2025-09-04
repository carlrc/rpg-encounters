from app.clients.openai_moderation import OpenAIModerationClient

CLIENT = OpenAIModerationClient()


# Test that borderline inappropriate content in the realm of role playing is not breaking OpenAI policy
async def test_moderation_flags_vulgar_content():
    test_text = "I don't give a fuck what you think"

    response = await CLIENT.moderate(test_text)
    categories = response.results[0].categories

    assert not categories.sexual
    assert not categories.harassment
    assert not categories.harassment_threatening
    assert not categories.violence


async def test_moderation_flags_sexual_content():
    test_text = "I want to fuck you"

    response = await CLIENT.moderate(test_text)
    categories = response.results[0].categories

    assert categories.sexual
    assert not categories.sexual_minors
    assert not categories.violence
    assert not categories.harassment_threatening
    assert not categories.violence


async def test_moderation_flags_mean_content():
    test_text = "I hate your kind. Dwarves are disgusting."

    response = await CLIENT.moderate(test_text)
    categories = response.results[0].categories

    assert categories.harassment
    assert not categories.harassment_threatening
    assert not categories.sexual
    assert not categories.sexual_minors
    assert not categories.violence
