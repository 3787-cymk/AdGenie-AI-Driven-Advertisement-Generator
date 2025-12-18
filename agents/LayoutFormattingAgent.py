"""
LayoutFormattingAgent module
"""

from pamphlet_agent import LayoutFormattingAgent as _CoreLayoutFormattingAgent


class _AgentMetadataMixin:
    """Provides a small manifest for observability dashboards."""

    manifest = {
        "name": "LayoutFormattingAgent",
        "role": "layout_renderer",
        "responsibilities": [
            "place text over background",
            "respect panel visibility flags",
            "coordinate with PamphletDesigner",
        ],
    }

    def metadata(self):
        return dict(self.manifest)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{self.manifest.get('name', self.__class__.__name__)} ready>"


class LayoutFormattingAgent(_AgentMetadataMixin, _CoreLayoutFormattingAgent):
    """
    Agent responsible for applying clean UI formatting:
    - positioning headline, body, features, and CTA
    - ensuring good readability on top of the background
    - respecting the "no solid background box behind text" requirement

    This simply re-uses the core implementation in `pamphlet_agent`.
    """

    pass


