from app.models.nugget import NuggetLayer, TrustNugget


class NuggetService:
    @staticmethod
    def select_response_by_trust(
        public_response: str,
        privileged_response: str | None,
        exclusive_response: str | None,
        total_trust: float,
        nugget: TrustNugget,
    ) -> tuple[str, NuggetLayer]:
        """
        Select appropriate response based on trust levels and nugget-specific thresholds.

        Args:
            public_response: Public level response
            privileged_response: Privileged level response (optional)
            exclusive_response: Exclusive level response (optional)
            total_trust: Current total trust level
            nugget: The nugget being used (contains threshold info)

        Returns:
            Tuple of (selected_response, response_level)
        """
        # Select response based on trust levels and nugget-specific thresholds
        if exclusive_response and total_trust >= nugget.get_threshold(
            NuggetLayer.EXCLUSIVE
        ):
            return exclusive_response, NuggetLayer.EXCLUSIVE
        elif privileged_response and total_trust >= nugget.get_threshold(
            NuggetLayer.PRIVILEGED
        ):
            return privileged_response, NuggetLayer.PRIVILEGED
        else:
            return public_response, NuggetLayer.PUBLIC
