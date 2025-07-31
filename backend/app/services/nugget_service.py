from typing import List
from app.models.nugget import (
    NuggetLayer,
    NUGGET_THRESHOLDS,
    TrustNugget,
    NuggetLevelInfo,
)
from app.models.trust import TrustState, TRUST_CHANGE_MAX, TOTAL_TRUST_MAX


class NuggetService:
    @staticmethod
    def get_trust_threshold(layer: NuggetLayer) -> float:
        """Get the trust threshold required for a nugget layer"""
        threshold_map = {
            NuggetLayer.PUBLIC: NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name],
            NuggetLayer.PRIVILEGED: NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name],
            NuggetLayer.EXCLUSIVE: NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name],
        }
        return threshold_map[layer]

    @staticmethod
    def categorize_nuggets_by_trust(
        trust_state: TrustState, all_nuggets: List[TrustNugget]
    ) -> List[NuggetLevelInfo]:
        """
        Categorize nuggets by trust level, returning structured information about each level.
        Returns list of NuggetLevelInfo objects with content, level, availability, and conditional availability.
        """
        nugget_levels = []
        current_trust = trust_state.total_trust
        max_possible_trust = min(TOTAL_TRUST_MAX, current_trust + TRUST_CHANGE_MAX)

        for nugget in all_nuggets:
            # Level 1 (PUBLIC) - always available (threshold 0.0)
            if nugget.level_1_content:
                nugget_levels.append(
                    NuggetLevelInfo(
                        content=nugget.level_1_content,
                        level=NuggetLayer.PUBLIC.name,
                        available=True,  # Always available
                        conditionally_available=False,
                        trust_needed=None,
                    )
                )

            # Level 2 (PRIVILEGED) - check availability and conditional availability
            if nugget.level_2_content:
                threshold = NuggetService.get_trust_threshold(NuggetLayer.PRIVILEGED)
                available = current_trust >= threshold
                conditionally_available = (
                    not available and max_possible_trust >= threshold
                )

                nugget_levels.append(
                    NuggetLevelInfo(
                        content=nugget.level_2_content,
                        level=NuggetLayer.PRIVILEGED.name,
                        available=available,
                        conditionally_available=conditionally_available,
                        trust_needed=threshold if conditionally_available else None,
                    )
                )

            # Level 3 (EXCLUSIVE) - check availability and conditional availability
            if nugget.level_3_content:
                threshold = NuggetService.get_trust_threshold(NuggetLayer.EXCLUSIVE)
                available = current_trust >= threshold
                conditionally_available = (
                    not available and max_possible_trust >= threshold
                )

                nugget_levels.append(
                    NuggetLevelInfo(
                        content=nugget.level_3_content,
                        level=NuggetLayer.EXCLUSIVE.name,
                        available=available,
                        conditionally_available=conditionally_available,
                        trust_needed=threshold if conditionally_available else None,
                    )
                )

        return nugget_levels

    @staticmethod
    def select_response_by_trust(
        public_response: str,
        privileged_response: str | None,
        exclusive_response: str | None,
        total_trust: float,
    ) -> tuple[str, NuggetLayer]:
        """
        Select appropriate response based on trust levels and trust adjustment.

        Args:
            agent_output: CharacterAgentOutput with public/privileged/exclusive responses
            current_trust: Current trust level before adjustment

        Returns:
            Tuple of (selected_response, response_level)
        """
        # Select response based on trust levels
        if exclusive_response and total_trust >= NuggetService.get_trust_threshold(
            NuggetLayer.EXCLUSIVE
        ):
            return exclusive_response, NuggetLayer.EXCLUSIVE
        elif privileged_response and total_trust >= NuggetService.get_trust_threshold(
            NuggetLayer.PRIVILEGED
        ):
            return privileged_response, NuggetLayer.PRIVILEGED
        else:
            return public_response, NuggetLayer.PUBLIC
