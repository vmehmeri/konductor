"""
Test fixture manifests for unit tests.
"""

SIMPLE_TOOL_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: Tool
metadata:
  name: test_tool
spec:
  type: pythonFunction
  description: A test tool
  source:
    file: "tools/test.py"
    functionName: "test_function"
  parameters:
    - name: "input"
      type: "string"
      description: "Test input"
"""

SIMPLE_MODEL_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: test_model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
  parameters:
    temperature: 0.7
"""

SIMPLE_AGENT_ONLY_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: test_agent
spec:
  modelRef: test_model
  instruction: "You are a test agent"
  toolRefs:
    - test_tool
"""

SIMPLE_AGENT_MANIFEST = f"""
{SIMPLE_MODEL_MANIFEST}
---
{SIMPLE_TOOL_MANIFEST}
---
{SIMPLE_AGENT_ONLY_MANIFEST}
"""

SEQUENTIAL_AGENT_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: SequentialAgent
metadata:
  name: test_sequential
spec:
  subAgentRefs:
    - test_agent
"""

LOOP_AGENT_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: LoopAgent
metadata:
  name: test_loop
spec:
  subAgentRefs:
    - test_agent
  maxIterations: 5
"""

PARALLEL_AGENT_MANIFEST = """
apiVersion: adk.google.com/v1alpha1
kind: ParallelAgent
metadata:
  name: test_parallel
spec:
  subAgentRefs:
    - test_agent1
    - test_agent2
"""

COMPLETE_MANIFEST = f"""
{SIMPLE_MODEL_MANIFEST}
---
{SIMPLE_TOOL_MANIFEST}
---
{SIMPLE_AGENT_ONLY_MANIFEST}
---
{SEQUENTIAL_AGENT_MANIFEST}
"""

COMPLETE_MANIFEST_WITH_NEW_AGENTS = f"""
{SIMPLE_MODEL_MANIFEST}
---
{SIMPLE_TOOL_MANIFEST}
---
{SIMPLE_AGENT_ONLY_MANIFEST}
---
{SEQUENTIAL_AGENT_MANIFEST}
---
{LOOP_AGENT_MANIFEST}
---
{PARALLEL_AGENT_MANIFEST}
"""

INVALID_MANIFEST_MISSING_FIELDS = """
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: invalid_agent
spec:
  instruction: "Missing modelRef"
"""

INVALID_MANIFEST_UNKNOWN_KIND = """
apiVersion: adk.google.com/v1alpha1
kind: UnknownKind
metadata:
  name: unknown
spec:
  field: value
"""
