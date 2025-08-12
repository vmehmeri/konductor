"""
Google ADK specific models and extensions.
"""

from typing import Any, Dict, Optional

from pydantic import Field

from ...core.models import ModelResource, ModelSpec


class GoogleAdkModelSpec(ModelSpec):
    """Google ADK specific model specification."""

    provider: str = Field(default="google", description="Provider is always 'google' for ADK")
    modelId: str = Field(description="Google model ID (e.g., 'gemini-2.5-flash')")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Model parameters like temperature, top_k, etc."
    )


class GoogleAdkModelResource(ModelResource):
    """Google ADK model resource."""

    spec: GoogleAdkModelSpec
