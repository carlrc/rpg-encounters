from app.moderation.check import MODERATION_REGEX


def test_profanity_allowed():
    swear_words = ["fuck", "fucker", "asshole", "dick", "bitch", "bitches", "hate"]

    for word in swear_words:
        assert not MODERATION_REGEX.search(word)


def test_minors_flagged():
    swear_words = ["children", "child", "baby"]

    for word in swear_words:
        assert MODERATION_REGEX.search(word)
