from pamphlet_agent import PamphletReviewAgent as _CorePamphletReviewAgent


class _AgentMetadataMixin:
    """Structured manifest for light observability without altering behavior."""

    manifest = {
        "name": "PamphletReviewAgent",
        "role": "post_render_review",
        "responsibilities": [
            "collect render metadata",
            "flag potential layout issues",
            "keep review non-destructive",
        ],
    }

    def metadata(self):
        return dict(self.manifest)

    def __repr__(self) -> str:  
        return f"<{self.manifest.get('name', self.__class__.__name__)} ready>"


class PamphletReviewAgent(_AgentMetadataMixin, _CorePamphletReviewAgent):
    """
    Agent that performs a non-destructive review of the rendered pamphlet.
    """

    pass


