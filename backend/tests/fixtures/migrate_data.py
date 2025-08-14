from sqlalchemy.orm import sessionmaker
from app.db.connection import DB_ENGINE
from app.db.models.player import PlayerORM
from tests.fixtures.players import players_db

def migrate_player_data():
    """Migrate player data from fixtures to database"""
    Session = sessionmaker(bind=DB_ENGINE)
    
    with Session() as session:
        # Check if data already exists
        existing_count = session.query(PlayerORM).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} players. Skipping migration.")
            return
        
        # Migrate fixture data
        for _, player in players_db.items():
            player_data = player.model_dump()
            # Remove the id since it will be auto-generated
            player_data.pop('id', None)
            
            player_orm = PlayerORM(**player_data)
            session.add(player_orm)
        
        session.commit()
        print(f"Successfully migrated {len(players_db)} players to database!")


if __name__ == "__main__":
    migrate_player_data()