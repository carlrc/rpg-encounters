from app.models.nugget import NuggetLayer, NUGGET_THRESHOLDS


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
