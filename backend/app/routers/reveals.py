from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.character_store import CharacterStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_db_session
from app.dependencies import get_current_user_world
from app.models.reveal import Reveal, RevealCreate, RevealUpdate

router = APIRouter(prefix="/api/reveals", tags=["reveals"])


@router.get("", response_model=List[Reveal])
def get_all_reveals(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all reveals across all characters"""
    user_id, world_id = user_world
    return RevealStore(user_id=user_id, world_id=world_id).get_all_reveals()


@router.post("", response_model=Reveal)
def create_reveal(
    reveal_data: RevealCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a reveal for multiple characters"""
    user_id, world_id = user_world

    with get_db_session() as session:
        # Verify all characters exist
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        for character_id in reveal_data.character_ids:
            if not character_store.character_exists(character_id):
                raise HTTPException(
                    status_code=404, detail=f"Character {character_id} not found"
                )

        return RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).create_reveal(reveal_data)


@router.get("/{reveal_id}", response_model=Reveal)
def get_reveal(
    reveal_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific reveal by ID"""
    user_id, world_id = user_world
    reveal = RevealStore(user_id=user_id, world_id=world_id).get_reveal(reveal_id)
    if not reveal:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return reveal


@router.get("/character/{character_id}", response_model=List[Reveal])
def get_character_reveals(
    character_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get all reveals for a character"""
    user_id, world_id = user_world

    with get_db_session() as session:
        # Verify character exists
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        if not character_store.character_exists(character_id):
            raise HTTPException(status_code=404, detail="Character not found")

        return RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).get_by_character_id(character_id)


@router.put("/{reveal_id}", response_model=Reveal)
def update_reveal(
    reveal_id: int,
    reveal_update: RevealUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update a reveal"""
    user_id, world_id = user_world

    with get_db_session() as session:
        # Verify all characters exist if character_ids are being updated
        if reveal_update.character_ids:
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            for character_id in reveal_update.character_ids:
                if not character_store.character_exists(character_id):
                    raise HTTPException(
                        status_code=404, detail=f"Character {character_id} not found"
                    )

        reveal = RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).update_reveal(reveal_id, reveal_update)
        if not reveal:
            raise HTTPException(status_code=404, detail="Reveal not found")
        return reveal


@router.delete("/{reveal_id}")
def delete_reveal(
    reveal_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a reveal"""
    user_id, world_id = user_world
    success = RevealStore(user_id=user_id, world_id=world_id).delete_reveal(reveal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return {"message": "Reveal deleted successfully"}
