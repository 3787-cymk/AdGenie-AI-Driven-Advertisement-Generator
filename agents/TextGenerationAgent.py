"""
TextGenerationAgent module
==========================

This module exposes the `TextGenerationAgent` used by the pamphlet generator
in a dedicated file for clarity and discoverability.

The core implementation lives in `pamphlet_agent.py` and is re-exported here
so there is a single source of truth and no duplication of logic.
"""

from pamphlet_agent import TextGenerationAgent as _CoreTextGenerationAgent


class _AgentMetadataMixin:
    """Minimal manifest for dashboards or debugging overlays."""

    manifest = {
        "name": "TextGenerationAgent",
        "role": "content_author",
        "responsibilities": [
            "headline",
            "description",
            "cta",
            "tagline",
        ],
    }

    def metadata(self):
        return dict(self.manifest)

    def __repr__(self) -> str: 
        return f"<{self.manifest.get('name', self.__class__.__name__)} ready>"


class TextGenerationAgent(_AgentMetadataMixin, _CoreTextGenerationAgent):
    """
    High-level agent responsible for generating structured pamphlet copy
    (headline, description, CTA, tagline) using Ollama via `OllamaTextGenerator`.
    """

    # Inherit all behavior from the core implementation.
    pass


