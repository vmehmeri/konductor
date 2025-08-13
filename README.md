
# Konductor: A declarative configuration engine for building AI Agents

Konductor is a modular, declarative configuration engine for building AI agents based on desired state, instead of code. It uses Kubernetes-like YAML manifests to generate fully functional agent applications.

Currently **focusing on Google's Agent Development Kit (ADK)** as the primary provider, with plans to expand to other AI agent frameworks.

![](./assets/konductor-demo.gif)

Instead of writing imperative Python code to define and connect agent components, users define agents and their tools in simple YAML manifests, using the familiar Kubernetes Resource Model (KRM). A code generator then "compiles" these manifests into fully runnable Python projects.

The vision for Konductor is for it to be a complete framework for declaring agent configurations across multiple AI frameworks, supporting diverse types of tools, connected data, and complex multi-agent architectures, with deployment capabilities to various agent runtimes.

End goal: Universal agent configuration that can target multiple frameworks and deployment environments.

-----

## 🏛️ Key Concepts

  * **Provider-Based Architecture**: Modular system supporting multiple AI agent frameworks through pluggable providers
  * **Declarative Manifests**: You define the *desired state* of your agent system in `.yaml` files. Each resource (like an `LlmAgent` or a `Tool`) has a `kind`, `metadata`, and a `spec`, just like in Kubernetes.
  * **Code Generation**: Provider-specific generators parse YAML manifests and use templates to generate framework-appropriate source code, wiring everything together automatically.

-----

## Features

- **Multi-Provider Support**: Extensible architecture supporting multiple AI frameworks (currently Google ADK)
- **YAML-to-Code Generation**: Convert simple YAML manifests into fully functional agent applications
- **Agent Configuration**: Define LLM agents with models, instructions, and tool references
- **Ready-to-Run Output**: Generated code includes a complete application structure with interactive CLI

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A Google API Key with the Gemini API enabled.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vmehmeri/konductor.git
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

Follow these steps to generate and run an agent:

```bash
# 1. Generate agent code from YAML manifest using the new CLI
uv run python -m konductor.cli generate examples/simple_agent_stack.yaml

# Or specify provider and output directory
uv run python -m konductor.cli generate -p google_adk -o my_agent examples/simple_agent_stack.yaml

# 2. Run the ADK web interface (for Google ADK provider)
uv run adk web 

# 4. Interact with your newly built agent!
```



## Project Structure

```
konductor/
├── konductor/                      # Core package
│   ├── core/                      # Provider-agnostic core components
│   │   ├── models.py             # Common resource models
│   │   ├── parser.py             # Universal manifest parser
│   │   └── generator.py          # Generation orchestrator
│   ├── providers/                 # Framework-specific implementations
│   │   ├── base.py               # Abstract provider interfaces
│   │   └── google_adk/           # Google ADK provider
│   │       ├── models.py         # ADK-specific models
│   │       ├── generator.py      # ADK code generator
│   │       └── templates/        # ADK Jinja2 templates
│   └── cli.py                    # Command-line interface
├── examples/                      # Example manifests
│   ├── simple_agent_stack.yaml   # Simple agent example
│   └── sequential_stack.yaml     # Multi-agent pipeline example
├── tools/                         # Example tool implementations
│   └── weather.py                # Example weather tool
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

### Model Definition

```yaml
apiVersion: adk.google.com/v1alpha1
kind: Model
metadata:
  name: gemini_flash_model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
  retryOptions:
    attempts: 2
    initialDelay: 5
  parameters:
    temperature: 0.7
```

### Agent Definition

```yaml
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: test_agent
spec:
  modelRef: gemini_flash_model
  instruction: "You are a helpful weather assistant."
  toolRefs:
    - weather-tool
```

## How It Works

1. **Parse**: The core parser reads your YAML manifest and validates it against Pydantic models
2. **Provider Selection**: Choose the target framework (currently Google ADK)
3. **Generate**: Provider-specific Jinja2 templates transform the parsed data into framework-appropriate code
4. **Structure**: The generator creates a complete application structure with:
   - Tool imports and mapping
   - Agent definitions with configured models and instructions
   - Interactive CLI runner for testing
5. **Run**: The generated application is ready to execute with the target framework

## Command Line Options

```bash
uv run python -m konductor.cli <command> [options]

Commands:
  generate              Generate code from manifest
  list-providers        List available providers
  dependencies          Show required dependencies

Generate Options:
  manifest_file         Path to the input YAML manifest file
  -p, --provider        Provider to use (default: google_adk)
  -o, --output-dir      Directory to save generated code (default: generated_agent)

Examples:
  uv run python -m konductor.cli generate examples/simple_agent_stack.yaml
  uv run python -m konductor.cli generate -p google_adk -o my_agent examples/simple_agent_stack.yaml
  uv run python -m konductor.cli list-providers
  uv run python -m konductor.cli dependencies -p google_adk
```

## Dependencies

### Core Dependencies
- `jinja2>=3.1.6` - Template engine for code generation
- `pydantic>=2.11.7` - Data validation for manifest parsing
- `pyyaml>=6.0.2` - YAML file parsing

### Provider-Specific Dependencies
- **Google ADK**: `google-adk>=1.10.0` - Google Agent Development Kit

### Development Dependencies (Optional)
```bash
# Install test dependencies
uv sync --extra test

# Install all development dependencies (includes black, pylint, isort, mypy, pytest)
uv sync --extra dev
```

## Testing

Konductor includes a comprehensive test suite built with pytest.

### Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=konductor

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run tests for specific components
uv run pytest tests/core/              # Core functionality tests
uv run pytest tests/providers/         # Provider tests
uv run pytest tests/test_cli.py        # CLI tests
```

### Test Structure

```
tests/
├── core/                       # Core component tests
│   ├── test_models.py         # Model validation tests
│   └── test_parser.py         # Parser functionality tests
├── providers/                  # Provider-specific tests
│   └── google_adk/
│       └── test_generator.py  # Google ADK generator tests
├── fixtures/                   # Test fixtures and data
├── test_cli.py                # CLI interface tests
└── test_integration.py        # End-to-end integration tests
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Victor Dantas

## Roadmap

### Current Focus: Google ADK Provider and Core Functionalities
We are currently focusing on providing the best possible experience for Google ADK users before expanding to other frameworks.

**Google ADK Enhancements:**
- [X] More agent/tool kinds: Support for LoopAgent and ParallelAgent
- [ ] Support for remote, authenticated tools
- [ ] Support for data kinds: SessionService, MemoryService, etc.
- [ ] Support for eval kinds: EvalJob, etc.
- [ ] Enhanced CLI: A dedicated command-line tool (`konduct`) with deployment capabilities
- [ ] Configuration validation and error handling, with proper reporting for malformed manifests
- [ ] Support for creating secrets via CLI (Google Secret Manager)
- [ ] Support for agent chaining and workflows
- [ ] Deployment Integration: The CLI directly calls `adk deploy` on the generated code (TBD: GCP environment bootstrapping)
- [ ] Reconciliation engine: The CLI handles deployment idempotently (requires state management and drift detection)

### Future: Multi-Provider Support (Not committed)
Once the Google ADK provider is mature, we plan to expand support to other AI agent frameworks:

- [ ] **OpenAI Agent Provider**: Support for OpenAI agents and tools
- [ ] **CrewAI Provider**: Multi-agent orchestration with CrewAI
- [ ] **AutoGen Provider**: Microsoft AutoGen framework support
- [ ] **Custom Providers**: Framework for building custom provider implementations

### Long-term Vision
- Universal agent configuration format 
- Advanced reconciliation engine for true GitOps workflows



