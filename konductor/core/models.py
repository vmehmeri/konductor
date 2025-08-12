"""
Provider-agnostic core models for Konductor.
"""
import yaml
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

class Metadata(BaseModel):
    """Common metadata for all resources."""
    name: str
    labels: Optional[Dict[str, str]] = Field(default_factory=dict)
    annotations: Optional[Dict[str, str]] = Field(default_factory=dict)

class ResourceSpec(BaseModel, ABC):
    """Base class for all resource specifications."""
    pass

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

class ModelSpec(ResourceSpec):
    """Base specification for model resources."""
    provider: str
    modelId: str
    parameters: Optional[Dict[str, Any]] = None

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
    toolRefs: Optional[List[str]] = Field(default_factory=list)  # Optional tools for sequential agents

class SequentialAgentResource(Resource):
    """Sequential agent resource definition."""
    kind: str = "SequentialAgent"
    spec: SequentialAgentSpec

# Registry of known resource types
RESOURCE_REGISTRY = {
    "Tool": ToolResource,
    "Model": ModelResource,
    "LlmModel": ModelResource,  # Backward compatibility
    "LlmAgent": LlmAgentResource,
    "SequentialAgent": SequentialAgentResource,
}

class ParsedManifest(BaseModel):
    """Container for parsed manifest resources."""
    tools: List[ToolResource] = Field(default_factory=list)
    models: List[ModelResource] = Field(default_factory=list)
    llm_agents: List[LlmAgentResource] = Field(default_factory=list)
    sequential_agents: List[SequentialAgentResource] = Field(default_factory=list)
    
    def get_all_agents(self) -> List[Union[LlmAgentResource, SequentialAgentResource]]:
        """Get all agent resources."""
        return self.llm_agents + self.sequential_agents
    
    def find_agent_by_name(self, name: str) -> Optional[Union[LlmAgentResource, SequentialAgentResource]]:
        """Find an agent by name."""
        for agent in self.get_all_agents():
            if agent.metadata.name == name:
                return agent
        return None