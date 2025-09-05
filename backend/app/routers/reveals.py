import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.character_store import CharacterStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_async_db_routes_session
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.reveal import Reveal, RevealCreate, RevealUpdate

router = APIRouter(prefix="/api/reveals", tags=["reveals"])

logger = logging.getLogger(__name__)


@router.get("", response_model=List[Reveal])
async def get_all_reveals(
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Get all reveals across all characters"""
    user_id, world_id = user_world
    try:
        return await RevealStore(user_id=user_id, world_id=world_id).get_all()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reveals for user {user_id}, world {world_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("", response_model=Reveal)
async def create_reveal(
    reveal_data: RevealCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Create a reveal for multiple characters"""
    user_id, world_id = user_world
    try:
        # Verify all characters exist
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        for character_id in reveal_data.character_ids:
            if not await character_store.exists(character_id):
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        return await RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).create(reveal_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create reveal for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{reveal_id}", response_model=Reveal)
async def get_reveal(
    reveal_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific reveal by ID"""
    user_id, world_id = user_world
    try:
        reveal = await RevealStore(user_id=user_id, world_id=world_id).get_reveal(
            reveal_id
        )
        if not reveal:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return reveal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get reveal {reveal_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/character/{character_id}", response_model=List[Reveal])
async def get_character_reveals(
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Get all reveals for a character"""
    user_id, world_id = user_world
    try:
        # Verify character exists
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        if not await character_store.exists(character_id):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        return await RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).get_by_character_id(character_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get reveals for character {character_id}, user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/{reveal_id}", response_model=Reveal)
async def update_reveal(
    reveal_id: int,
    reveal_update: RevealUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
    session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Update a reveal"""
    user_id, world_id = user_world
    try:
        # Verify all characters exist if character_ids are being updated
        if reveal_update.character_ids:
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            for character_id in reveal_update.character_ids:
                if not await character_store.exists(character_id):
                    raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        reveal = await RevealStore(
            user_id=user_id, world_id=world_id, session=session
        ).update(reveal_id, reveal_update)
        if not reveal:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return reveal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update reveal {reveal_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{reveal_id}")
async def delete_reveal(
    reveal_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a reveal"""
    user_id, world_id = user_world
    try:
        success = await RevealStore(user_id=user_id, world_id=world_id).delete(
            reveal_id
        )
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return {"message": "Reveal deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete reveal {reveal_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
