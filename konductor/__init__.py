"""
Konductor: A declarative configuration engine for building AI Agents.
"""

from .core.generator import KonductorGenerator
from .core.models import ParsedManifest
from .core.parser import ManifestParser
from .providers.base import provider_registry

# Register providers
from .providers.google_adk.generator import GoogleAdkGenerator

# Register Google ADK provider
provider_registry.register("google_adk", GoogleAdkGenerator())

__version__ = "0.1.0"
__all__ = ["KonductorGenerator", "ManifestParser", "ParsedManifest"]
