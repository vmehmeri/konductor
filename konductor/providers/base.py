"""
Base classes for provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..core.models import ParsedManifest


class CodeGenerator(ABC):
    """Abstract base class for provider-specific code generators."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def generate_code(
        self, manifest: ParsedManifest, output_dir: str, **kwargs: Any
    ) -> Dict[str, str]:
        """
        Generate code from a parsed manifest.

        Args:
            manifest: Parsed manifest containing resources
            output_dir: Directory to output generated code
            **kwargs: Additional provider-specific options

        Returns:
            Dictionary mapping file paths to generated content
        """
        pass

    @abstractmethod
    def get_required_dependencies(self) -> List[str]:
        """Get list of required dependencies for this provider."""
        pass

    @abstractmethod
    def validate_manifest_for_provider(self, manifest: ParsedManifest) -> List[str]:
        """
        Validate manifest for provider-specific requirements.

        Returns:
            List of validation error messages
        """
        pass

    def get_template_context(self, manifest: ParsedManifest, **kwargs: Any) -> Dict[str, Any]:
        """Build template context from manifest."""
        return {
            "tools": manifest.tools,
            "models": manifest.models,
            "llm_agents": manifest.llm_agents,
            "sequential_agents": manifest.sequential_agents,
            **kwargs,
        }


class ProviderRegistry:
    """Registry for provider implementations."""

    def __init__(self) -> None:
        self._providers: Dict[str, CodeGenerator] = {}

    def register(self, name: str, generator: CodeGenerator) -> None:
        """Register a provider."""
        self._providers[name] = generator

    def get(self, name: str) -> CodeGenerator:
        """Get a provider by name."""
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}")
        return self._providers[name]

    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())


# Global provider registry
provider_registry = ProviderRegistry()
