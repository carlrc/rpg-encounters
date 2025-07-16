from app.models.memory import Memory

memories_db = {
    1: Memory(
        id=1,
        title="The Garden Vandal Mystery",
        linked_character_ids=[1, 2, 3, 4],
        visibility_type="always",
        keywords=[],
        player_races=[],
        player_alignments=[],
        memory_text="Someone has been destroying the village gardens at night! Vegetables trampled, flowers uprooted, and prize-winning plants ruined. Nobody knows who's doing it, but the whole village is talking about it.",
        character_limit=500
    ),
    2: Memory(
        id=2,
        title="Suspicious Footprints",
        linked_character_ids=[4],
        visibility_type="keyword",
        keywords=["footprints", "tracks", "evidence", "clues", "investigation"],
        player_races=[],
        player_alignments=[],
        memory_text="Small hobbit-sized footprints were found near the destroyed gardens. Some say they look familiar, but nobody wants to accuse their neighbors without proof.",
        character_limit=500
    ),
    3: Memory(
        id=3,
        title="The Tavern Gossip",
        linked_character_ids=[1],
        visibility_type="keyword",
        keywords=["gossip", "rumors", "tavern", "whispers", "speculation"],
        player_races=[],
        player_alignments=[],
        memory_text="The tavern is buzzing with theories about the garden destroyer. Some suspect jealousy over the annual garden competition, others think it's just mischief. Everyone has an opinion but no real answers.",
        character_limit=500
    ),
    4: Memory(
        id=4,
        title="The Competition Connection",
        linked_character_ids=[2, 4],
        visibility_type="keyword",
        keywords=["competition", "contest", "jealousy", "rivalry", "prize"],
        player_races=[],
        player_alignments=[],
        memory_text="The garden destruction seems to target the best gardens - those that usually win the annual village competition. Could someone be eliminating the competition through sabotage?",
        character_limit=500
    )
}

next_memory_id = 5
