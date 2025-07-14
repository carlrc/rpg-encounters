from typing import Optional, List
from ..models.player import Player, PlayerCreate, PlayerUpdate

players_db = {
    1: Player(
        id=1,
        name="Aragorn",
        appearance="Tall ranger with weathered features, keen grey eyes, and dark hair",
        race="Human",
        class_name="Ranger",
        size="Medium",
        alignment="Lawful Good",
        tags=["#fellowship", "#rangers-of-the-north"]
    ),
    2: Player(
        id=2,
        name="Legolas",
        appearance="Graceful elf with golden hair, bright blue eyes, and elegant features",
        race="Elf",
        class_name="Ranger",
        size="Medium",
        alignment="Chaotic Good",
        tags=["#fellowship", "#woodland-realm"]
    ),
    3: Player(
        id=3,
        name="Gimli",
        appearance="Stout dwarf with braided red beard, chainmail armor, and fierce eyes",
        race="Dwarf",
        class_name="Fighter",
        size="Medium",
        alignment="Lawful Good",
        tags=["#fellowship", "#erebor"]
    ),
    4: Player(
        id=4,
        name="Gandalf",
        appearance="Tall wizard in grey robes with long white beard and piercing eyes",
        race="Human",
        class_name="Wizard",
        size="Medium",
        alignment="Neutral Good",
        tags=["#fellowship", "#istari"]
    )
}
next_player_id = 5

class PlayerStore:
    def __init__(self):
        self.players = players_db
        self.next_id = next_player_id

    def get_all_players(self) -> List[Player]:
        """Get all players"""
        return list(self.players.values())

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Get a specific player by ID"""
        return self.players.get(player_id)

    def create_player(self, player_data: PlayerCreate) -> Player:
        """Create a new player"""
        player_dict = player_data.model_dump()
        player_dict["id"] = self.next_id
        
        new_player = Player(**player_dict)
        self.players[self.next_id] = new_player
        self.next_id += 1
        
        return new_player

    def update_player(self, player_id: int, player_update: PlayerUpdate) -> Optional[Player]:
        """Update an existing player"""
        if player_id not in self.players:
            return None
        
        existing_player = self.players[player_id]
        update_data = player_update.model_dump(exclude_unset=True)
        
        # Update the existing player with new data
        updated_data = existing_player.model_dump()
        updated_data.update(update_data)
        
        updated_player = Player(**updated_data)
        self.players[player_id] = updated_player
        
        return updated_player

    def delete_player(self, player_id: int) -> bool:
        """Delete a player"""
        if player_id not in self.players:
            return False
        
        del self.players[player_id]
        return True

    def player_exists(self, player_id: int) -> bool:
        """Check if a player exists"""
        return player_id in self.players


# Create a singleton instance
player_store = PlayerStore()
