from app.models.nugget import TruthLayer, Truth


class TruthService:
    @staticmethod
    def select_response_by_trust(
        public_response: str,
        privileged_response: str | None,
        exclusive_response: str | None,
        total_trust: float,
        truth: Truth,
    ) -> tuple[str, TruthLayer]:
        """
        Select appropriate response based on trust levels and truth-specific thresholds.

        Args:
            public_response: Public level response
            privileged_response: Privileged level response (optional)
            exclusive_response: Exclusive level response (optional)
            total_trust: Current total trust level
            truth: The truth being used (contains threshold info)

        Returns:
            Tuple of (selected_response, response_level)
        """
        # Select response based on trust levels and truth-specific thresholds
        if exclusive_response and total_trust >= truth.get_threshold(
            TruthLayer.EXCLUSIVE
        ):
            return exclusive_response, TruthLayer.EXCLUSIVE
        elif privileged_response and total_trust >= truth.get_threshold(
            TruthLayer.PRIVILEGED
        ):
            return privileged_response, TruthLayer.PRIVILEGED
        else:
            return public_response, TruthLayer.PUBLIC
