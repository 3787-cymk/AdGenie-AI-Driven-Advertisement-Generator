"""
ContentEditingAgent module
==========================

Provides a project-specific wrapper for the `ContentEditingAgent` that is
implemented in `pamphlet_agent.py`. This keeps responsibilities clear:

- TextGenerationAgent  → create initial content
- ContentEditingAgent  → refine tone, grammar, formatting, and length
"""

from pamphlet_agent import ContentEditingAgent as _CoreContentEditingAgent


class _AgentMetadataMixin:
    """Lightweight metadata/introspection helpers for UI/debug panels."""

    manifest = {
        "name": "ContentEditingAgent",
        "role": "text_refiner",
        "responsibilities": [
            "normalize whitespace",
            "limit headline length",
            "trim long descriptions for layout fit",
        ],
    }

    def metadata(self):
        return dict(self.manifest)

    def __repr__(self) -> str: 
        return f"<{self.manifest.get('name', self.__class__.__name__)} ready>"


class ContentEditingAgent(_AgentMetadataMixin, _CoreContentEditingAgent):
    """
    Agent that post-processes generated pamphlet text to make it more suitable
    for the visual layout (shorter, cleaner, better formatted).
    """
    # The metadata mixin simply exposes a structured manifest for diagnostics.


