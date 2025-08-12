# parser.py
import yaml
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# Pydantic models to validate the structure of the YAML manifest

class Metadata(BaseModel):
    name: str

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class ToolSource(BaseModel):
    file: str
    functionName: str

class ToolSpec(BaseModel):
    type: Literal["pythonFunction"]
    description: str
    source: ToolSource
    parameters: List[ToolParameter]

class ToolResource(BaseModel):
    apiVersion: str
    kind: Literal["Tool"]
    metadata: Metadata
    spec: ToolSpec

class LlmAgentSpec(BaseModel):
    model: str
    instruction: str
    toolRefs: Optional[List[str]] = Field(default_factory=list)

class LlmAgentResource(BaseModel):
    apiVersion: str
    kind: Literal["LlmAgent"]
    metadata: Metadata
    spec: LlmAgentSpec

def parse_manifest(file_path: str) -> (List[LlmAgentResource], List[ToolResource]):
    """Parses a YAML manifest file into lists of agent and tool resources."""
    agents = []
    tools = []
    with open(file_path, 'r') as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if not doc:
                continue
            kind = doc.get("kind")
            if kind == "LlmAgent":
                agents.append(LlmAgentResource(**doc))
            elif kind == "Tool":
                tools.append(ToolResource(**doc))
            else:
                print(f"Warning: Unknown kind '{kind}' found in manifest. Skipping.")
    print(f"Parsed {len(agents)} agent(s) and {len(tools)} tool(s).")
    return agents, tools

