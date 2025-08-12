# parser.py
import yaml
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any, Optional

# --- Pydantic Models ---
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

class LlmModelSpec(BaseModel):
    provider: str = "google"
    modelId: str
    parameters: Optional[Dict[str, Any]] = None

class LlmModelResource(BaseModel):
    apiVersion: str
    kind: Literal["LlmModel"]
    metadata: Metadata
    spec: LlmModelSpec
    
class LlmAgentSpec(BaseModel):
    modelRef: str # Changed from 'model'
    instruction: str
    toolRefs: Optional[List[str]] = Field(default_factory=list)
    output_key: Optional[str] = None

class LlmAgentResource(BaseModel):
    apiVersion: str
    kind: Literal["LlmAgent"]
    metadata: Metadata
    spec: LlmAgentSpec

class SequentialAgentSpec(BaseModel):
    subAgentRefs: List[str]

class SequentialAgentResource(BaseModel):
    apiVersion: str
    kind: Literal["SequentialAgent"]
    metadata: Metadata
    spec: SequentialAgentSpec

# --- Parsing Function ---
def parse_manifest(file_path: str) -> (List[LlmAgentResource], List[SequentialAgentResource], List[ToolResource], List[LlmModelResource]):
    """Parses a YAML manifest file into lists of agent, tool, and model resources."""
    llm_agents = []
    sequential_agents = []
    tools = []
    llm_models = []
    
    with open(file_path, 'r') as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if not doc:
                continue
            kind = doc.get("kind")
            if kind == "LlmAgent":
                llm_agents.append(LlmAgentResource(**doc))
            elif kind == "SequentialAgent":
                sequential_agents.append(SequentialAgentResource(**doc))
            elif kind == "Tool":
                tools.append(ToolResource(**doc))
            elif kind == "LlmModel": # <-- Handle the new kind
                llm_models.append(LlmModelResource(**doc))
            else:
                print(f"Warning: Unknown kind '{kind}' found in manifest. Skipping.")
                
    print(f"Parsed {len(llm_agents)} LlmAgent(s), {len(sequential_agents)} SequentialAgent(s), {len(tools)} tool(s), and {len(llm_models)} LlmModel(s).")
    return llm_agents, sequential_agents, tools, llm_models