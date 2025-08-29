import logging
from typing import List

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy import Engine

from app.data.base_store import BaseStore
from app.db.connection import get_db_engine
from app.db.models.conversation import ConversationORM
from app.models.conversation import Conversation, ConversationCreate

logger = logging.getLogger(__name__)


class ConversationStore(BaseStore):
    def __init__(
        self,
        user_id: int,
        world_id: int,
        engine: Engine = get_db_engine(),
        session=None,
    ):
        super().__init__(
            user_id=user_id, world_id=world_id, engine=engine, session=session
        )

    def create(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        with self.get_session() as session:
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
            session.flush()
            session.refresh(conversation_orm)

            return self._orm_to_conversation(conversation_orm)

    def get(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> Conversation | None:
        with self.get_session() as session:
            conversation_orm = (
                session.query(ConversationORM)
                .filter(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
                .first()
            )

            if not conversation_orm:
                return None

            return self._orm_to_conversation(conversation_orm)

    def add_messages(
        self,
        player_id: int,
        character_id: int,
        encounter_id: int,
        new_messages: List[ModelMessage],
    ) -> Conversation | None:
        """
        Append messages to an existing conversation.
        """
        with self.get_session() as session:
            # Find existing conversation
            conversation_orm = (
                session.query(ConversationORM)
                .filter(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
                .first()
            )

            if not conversation_orm:
                logger.warning(
                    f"Could not find conversation for player_id={player_id}, character_id={character_id}, encounter_id={encounter_id}, user_id={self.user_id}, world_id={self.world_id}"
                )
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
            session.flush()
            session.refresh(conversation_orm)

            return self._orm_to_conversation(conversation_orm)

    def conversation_exists(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> bool:
        """Check if a conversation exists."""
        with self.get_session() as session:
            conversation_orm = (
                session.query(ConversationORM)
                .filter(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
                .first()
            )
            return conversation_orm is not None

    def delete_conversation(
        self, player_id: int, character_id: int, encounter_id: int
    ) -> bool:
        """Delete a conversation."""
        with self.get_session() as session:
            conversation_orm = (
                session.query(ConversationORM)
                .filter(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == self.user_id,
                    ConversationORM.world_id == self.world_id,
                )
                .first()
            )

            if not conversation_orm:
                return False

            session.delete(conversation_orm)
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
