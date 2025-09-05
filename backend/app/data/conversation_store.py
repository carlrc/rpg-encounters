import logging
from typing import List

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.base_store import BaseStore
from app.db.models.conversation import ConversationORM
from app.models.conversation import Conversation, ConversationCreate

logger = logging.getLogger(__name__)


class ConversationStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        session: AsyncSession = None,
    ):
        super().__init__(user_id=user_id, world_id=world_id, session=session)

    async def create(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        async with self.get_session() as session:
            # Serialize messages to JSON bytes
            messages_json = (
                ModelMessagesTypeAdapter.dump_json(conversation_data.messages)
                if conversation_data.messages
                else None
            )

            conversation_orm = ConversationORM(
                user_id=self.user_id,
                world_id=self.world_id,
                player_id=conversation_data.player_id,
                character_id=conversation_data.character_id,
                encounter_id=conversation_data.encounter_id,
                messages=messages_json,
            )
            session.add(conversation_orm)
            await session.flush()
            await session.refresh(conversation_orm)

            return self._orm_to_conversation(conversation_orm)

    async def get(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> Conversation | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(ConversationORM).where(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
            )
            conversation_orm = result.scalars().first()

            if not conversation_orm:
                return None

            return self._orm_to_conversation(conversation_orm)

    async def add_messages(
        self,
        player_id: int,
        character_id: int,
        encounter_id: int,
        new_messages: List[ModelMessage],
    ) -> Conversation | None:
        """
        Append messages to an existing conversation.
        """
        async with self.get_session() as session:
            # Find existing conversation
            result = await session.execute(
                select(ConversationORM).where(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
            )
            conversation_orm = result.scalars().first()

            if not conversation_orm:
                return None

            # Deserialize existing messages
            existing_messages = (
                ModelMessagesTypeAdapter.validate_json(conversation_orm.messages)
                if conversation_orm.messages
                else []
            )
            # Combine and serialize back
            conversation_orm.messages = ModelMessagesTypeAdapter.dump_json(
                existing_messages + new_messages
            )
            await session.flush()
            await session.refresh(conversation_orm)

            return self._orm_to_conversation(conversation_orm)

    async def exists(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> bool:
        """Check if a conversation exists."""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConversationORM).where(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
            )
            conversation_orm = result.scalars().first()
            return conversation_orm is not None

    async def delete(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> bool:
        """Delete a conversation."""
        async with self.get_session() as session:
            result = await session.execute(
                select(ConversationORM).where(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
            )
            conversation_orm = result.scalars().first()

            if not conversation_orm:
                return False

            await session.delete(conversation_orm)
            return True

    def _orm_to_conversation(self, conversation_orm: ConversationORM) -> Conversation:
        """Convert ConversationORM to Conversation model"""
        # Deserialize the bytes back to ModelMessage objects
        messages = (
            ModelMessagesTypeAdapter.validate_json(conversation_orm.messages)
            if conversation_orm.messages
            else []
        )

        return Conversation(
            id=conversation_orm.id,
            player_id=conversation_orm.player_id,
            character_id=conversation_orm.character_id,
            encounter_id=conversation_orm.encounter_id,
            messages=messages,
        )
