from typing import Optional, List
from app.models.player import Player, PlayerCreate, PlayerUpdate
from tests.fixtures.players import players_db, next_player_id


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

    def update_player(
        self, player_id: int, player_update: PlayerUpdate
    ) -> Optional[Player]:
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
