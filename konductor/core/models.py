"""
Provider-agnostic core models for Konductor.
"""

from abc import ABC
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Common metadata for all resources."""

    name: str
    labels: Optional[Dict[str, str]] = Field(default_factory=dict)
    annotations: Optional[Dict[str, str]] = Field(default_factory=dict)


class ResourceSpec(BaseModel, ABC):
    """Base class for all resource specifications."""


class Resource(BaseModel, ABC):
    """Base class for all Konductor resources."""

    apiVersion: str
    kind: str
    metadata: Metadata
    spec: ResourceSpec


class ToolParameter(BaseModel):
    """Parameter definition for tools."""

    name: str
    type: str
    description: str
    required: bool = True


class ToolSource(BaseModel):
    """Source reference for tool implementations."""

    file: str
    functionName: str


class ToolSpec(ResourceSpec):
    """Specification for tool resources."""

    type: str = "pythonFunction"
    description: str
    source: ToolSource
    parameters: List[ToolParameter]


class ToolResource(Resource):
    """Tool resource definition."""

    kind: str = "Tool"
    spec: ToolSpec


class RetryOptions(BaseModel):
    """Retry configuration for model requests."""

    attempts: Optional[int] = None
    initialDelay: Optional[float] = None
    maxDelay: Optional[float] = None
    expBase: Optional[float] = None
    jitter: Optional[float] = None
    httpStatusCodes: Optional[List[int]] = None


class ModelSpec(ResourceSpec):
    """Base specification for model resources."""

    provider: str
    modelId: str
    parameters: Optional[Dict[str, Any]] = None
    retryOptions: Optional[RetryOptions] = None


class ModelResource(Resource):
    """Model resource definition."""

    kind: str = "Model"
    spec: ModelSpec


class AgentSpec(ResourceSpec):
    """Base specification for agent resources."""

    instruction: str
    toolRefs: Optional[List[str]] = Field(default_factory=list)


class LlmAgentSpec(AgentSpec):
    """Specification for LLM agent resources."""

    modelRef: str
    output_key: Optional[str] = None


class LlmAgentResource(Resource):
    """LLM agent resource definition."""

    kind: str = "LlmAgent"
    spec: LlmAgentSpec


class SequentialAgentSpec(ResourceSpec):
    """Specification for sequential agent resources."""

    subAgentRefs: List[str]
    toolRefs: Optional[List[str]] = Field(
        default_factory=list
    )  # Optional tools for sequential agents


class SequentialAgentResource(Resource):
    """Sequential agent resource definition."""

    kind: str = "SequentialAgent"
    spec: SequentialAgentSpec


class LoopAgentSpec(ResourceSpec):
    """Specification for loop agent resources."""

    subAgentRefs: List[str]
    maxIterations: Optional[int] = None


class LoopAgentResource(Resource):
    """Loop agent resource definition."""

    kind: str = "LoopAgent"
    spec: LoopAgentSpec


class ParallelAgentSpec(ResourceSpec):
    """Specification for parallel agent resources."""

    subAgentRefs: List[str]


class ParallelAgentResource(Resource):
    """Parallel agent resource definition."""

    kind: str = "ParallelAgent"
    spec: ParallelAgentSpec


# Registry of known resource types
RESOURCE_REGISTRY: Dict[str, Type[Resource]] = {
    "Tool": ToolResource,
    "Model": ModelResource,
    "LlmModel": ModelResource,  # Backward compatibility
    "LlmAgent": LlmAgentResource,
    "SequentialAgent": SequentialAgentResource,
    "LoopAgent": LoopAgentResource,
    "ParallelAgent": ParallelAgentResource,
}


class ParsedManifest(BaseModel):
    """Container for parsed manifest resources."""

    tools: List[ToolResource] = Field(default_factory=list)
    models: List[ModelResource] = Field(default_factory=list)
    llm_agents: List[LlmAgentResource] = Field(default_factory=list)
    sequential_agents: List[SequentialAgentResource] = Field(default_factory=list)
    loop_agents: List[LoopAgentResource] = Field(default_factory=list)
    parallel_agents: List[ParallelAgentResource] = Field(default_factory=list)

    def get_all_agents(
        self,
    ) -> List[
        Union[LlmAgentResource, SequentialAgentResource, LoopAgentResource, ParallelAgentResource]
    ]:
        """Get all agent resources."""
        return self.llm_agents + self.sequential_agents + self.loop_agents + self.parallel_agents

    def find_agent_by_name(
        self, name: str
    ) -> Optional[
        Union[LlmAgentResource, SequentialAgentResource, LoopAgentResource, ParallelAgentResource]
    ]:
        """Find an agent by name."""
        for agent in self.get_all_agents():
            if agent.metadata.name == name:
                return agent
        return None
