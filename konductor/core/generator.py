"""
Main code generation orchestrator for Konductor.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..providers.base import CodeGenerator

from ..providers.base import provider_registry
from .models import ParsedManifest
from .parser import ManifestParser


class KonductorGenerator:
    """Main generator that orchestrates provider-specific code generation."""

    def __init__(self, provider: str = "google_adk") -> None:
        self.provider_name = provider
        self.parser = ManifestParser()

        # Lazy load provider to avoid import issues
        self._provider: Optional["CodeGenerator"] = None

    @property
    def provider(self) -> "CodeGenerator":
        """Get the provider instance, loading it if necessary."""
        if self._provider is None:
            self._provider = provider_registry.get(self.provider_name)
        return self._provider

    def generate_from_manifest(
        self, manifest_path: str, output_dir: str = "generated_agent", **kwargs: Any
    ) -> Dict[str, str]:
        """
        Generate code from a manifest file.

        Args:
            manifest_path: Path to the YAML manifest file
            output_dir: Directory to output generated code
            **kwargs: Additional provider-specific options

        Returns:
            Dictionary mapping file paths to generated content
        """
        # Parse the manifest
        manifest = self.parser.parse_manifest(manifest_path)

        # Validate the manifest
        validation_errors = self.parser.validate_manifest(manifest)
        if validation_errors:
            raise ValueError(f"Manifest validation failed:\n" + "\n".join(validation_errors))

        # Provider-specific validation
        provider_errors = self.provider.validate_manifest_for_provider(manifest)
        if provider_errors:
            raise ValueError(f"Provider validation failed:\n" + "\n".join(provider_errors))

        # Generate code
        print(f"Generating code using provider: {self.provider_name}")
        generated_files = self.provider.generate_code(manifest, output_dir, **kwargs)

        print(f"\nCode generation complete. Files are in '{output_dir}' directory.")
        return generated_files  # type: ignore[no-any-return]

    def get_required_dependencies(self) -> Dict[str, Any]:
        """Get information about required dependencies."""
        return {
            "provider": self.provider_name,
            "dependencies": self.provider.get_required_dependencies(),
        }

    def list_available_providers(self) -> List[str]:
        """List all available providers."""
        return provider_registry.list_providers()
