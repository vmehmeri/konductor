
# Konductor: A declarative configuration engine for building AI Agents

Konductor is a declarative, Kubernetes-like configuration engine for building and deploying AI agents with Google's Agent Development Kit (ADK).

Instead of writing imperative Python code to define and connect agent components, users define agents and their tools in simple YAML manifests, using the familiar Kubernetes Resource Model (KRM). A code generator then "compiles" these manifests into a fully runnable ADK Python project.

The vision for Konductor is for it to be a complete framework for declaring agent configurations, including tools, connected data, and complex multi-agent architectures, and deploying agents to an Agent runtime (Agent Engine on Google Cloud) via a control-plane CLI utility `adkctl` (WIP). 

End goal: `adkctl apply -f <manifest>.yaml` -> Agent up and running in Agent Engine.

-----

## 🏛️ Key Concepts

  * **Declarative Manifests**: You define the *desired state* of your agent system in `.yaml` files. Each resource (like an `LlmAgent` or a `Tool`) has a `kind`, `metadata`, and a `spec`, just like in Kubernetes.
  * **Code Generation**: The `generator.py` script acts as a simple control plane. It parses the YAML manifest and uses templates to generate the necessary ADK Python source code, wiring everything together automatically.

-----

## Features

- **YAML-to-Code Generation**: Convert simple YAML manifests into fully functional ADK Python applications
- **Tool Integration**: Automatically wire up custom Python functions as agent tools
- **Agent Configuration**: Define LLM agents with models, instructions, and tool references
- **Ready-to-Run Output**: Generated code includes a complete application structure with interactive CLI

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A Google API Key with the Gemini API enabled.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/konductor.git
cd konductor
```

2. Install dependencies using uv:
```bash
uv lock
```

3. Set your API key:
```bash
export GOOGLE_API_KEY=<your-api-key>
```

## Quick Start

Follow these steps to generate and run an ADK agent:

```bash
# 1. Lock dependencies
uv lock 

# 2. Generate agent code from YAML manifest
uv run python konductor/generator.py simple_agent_stack.yaml

# 3. Activate the virtual environment
. .venv/bin/activate

# 4. Run the ADK web interface
adk web 

# 5. Interact with your newly built agent!
```


## Project Structure

```
konductor/
├── konductor/              # Core generator package
│   ├── generator.py        # Code generation logic with Jinja2 templates
│   └── parser.py          # YAML manifest parser with Pydantic models
├── tools/                  # Directory for example custom tool implementations
│   └── weather.py         # Example weather tool
└── simple_agent_stack.yaml # Example manifest file
```

## Manifest Format

Konductor uses YAML manifests to define agents and tools. Here's the structure:

### Tool Definition

```yaml
apiVersion: adk.google.com/v1alpha1
kind: Tool
metadata:
  name: weather-tool
spec:
  type: pythonFunction
  description: A tool to fetch weather information.
  source:
    file: "tools/weather.py"
    functionName: "get_weather_report"
  parameters:
    - name: "city"
      type: "string"
      description: "The name of the city."
```

### Agent Definition

```yaml
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: test_agent
spec:
  model: "gemini-2.5-flash"
  instruction: "You are a helpful weather assistant."
  toolRefs:
    - weather-tool
```

## How It Works

1. **Parse**: The parser reads your YAML manifest and validates it against Pydantic models
2. **Generate**: Jinja2 templates transform the parsed data into Python code
3. **Structure**: The generator creates a complete ADK application structure with:
   - Tool imports and mapping
   - Agent definitions with configured models and instructions
   - Interactive CLI runner for testing
4. **Run**: The generated application is ready to execute with ADK


## Command Line Options

```bash
uv run python konductor/generator.py [options] <manifest_file>

Arguments:
  manifest_file          Path to the input YAML manifest file

Options:
  -o, --output-dir DIR   Directory to save generated code (default: generated_agent)
```

## Dependencies

- `google-adk>=1.10.0` - Google Agent Development Kit
- `jinja2>=3.1.6` - Template engine for code generation
- `pydantic>=2.11.7` - Data validation for manifest parsing
- `pyyaml>=6.0.2` - YAML file parsing

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Victor Dantas

## Roadmap

- [ ] More agent/tool kinds: Support for LoopAgent, and ToolSet
- [ ] Support for remote, authenticated tools
- [ ] Support for data kinds: SessionService, MemoryService, etc.
- [ ] Support for eval kinds: EvalJob, etc.
- [ ] A Robust CLI: A dedicated command-line tool (adkctl) to replace the Python scripts.
- [ ] Configuration validation and error handling, with proper reporting for malformed manifests.
- [ ] Support for creating secrets via CLI (Google Secret Manager)
- [ ] Support for agent chaining and workflows
- [ ] Deployment Integration: The CLI could directly call adk deploy on the generated code


