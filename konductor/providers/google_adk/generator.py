"""
Google ADK specific code generator.
"""

import os
from collections import defaultdict, deque
from typing import Any, Dict, List, Union

from jinja2 import Environment, FileSystemLoader

from ...core.models import (
    LlmAgentResource,
    LoopAgentResource,
    ParallelAgentResource,
    ParsedManifest,
    SequentialAgentResource,
)
from ...core.parser import ManifestParser
from ..base import CodeGenerator

# Type alias for all agent types
AgentResource = Union[
    LlmAgentResource, SequentialAgentResource, LoopAgentResource, ParallelAgentResource
]


class GoogleAdkGenerator(CodeGenerator):
    """Code generator for Google ADK framework."""

    def __init__(self) -> None:
        super().__init__("google_adk")
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def _topological_sort_agents(self, manifest: ParsedManifest) -> Dict[str, List]:
        """Sort agents topologically based on their dependencies."""
        # Create a mapping from agent name to agent object
        all_agents: Dict[str, AgentResource] = {}
        for llm_agent in manifest.llm_agents:
            all_agents[llm_agent.metadata.name] = llm_agent
        for seq_agent in manifest.sequential_agents:
            all_agents[seq_agent.metadata.name] = seq_agent
        for loop_agent in manifest.loop_agents:
            all_agents[loop_agent.metadata.name] = loop_agent
        for parallel_agent in manifest.parallel_agents:
            all_agents[parallel_agent.metadata.name] = parallel_agent

        # Build dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize all agents with in-degree 0
        for agent_name in all_agents:
            in_degree[agent_name] = 0

        # Build the dependency graph (agent -> depends on sub_agents)
        for agent_name, agent in all_agents.items():
            if hasattr(agent.spec, "subAgentRefs"):
                for sub_agent_ref in agent.spec.subAgentRefs:
                    if sub_agent_ref in all_agents:
                        graph[sub_agent_ref].append(agent_name)
                        in_degree[agent_name] += 1

        # Topological sort using Kahn's algorithm
        queue = deque([agent for agent in all_agents if in_degree[agent] == 0])
        sorted_agents = []

        while queue:
            current = queue.popleft()
            sorted_agents.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(sorted_agents) != len(all_agents):
            raise ValueError("Circular dependency detected in agent references")

        # Group sorted agents by type
        sorted_llm_agents: List[LlmAgentResource] = []
        sorted_sequential_agents: List[SequentialAgentResource] = []
        sorted_loop_agents: List[LoopAgentResource] = []
        sorted_parallel_agents: List[ParallelAgentResource] = []

        for agent_name in sorted_agents:
            agent = all_agents[agent_name]
            if isinstance(agent, LlmAgentResource):
                sorted_llm_agents.append(agent)
            elif isinstance(agent, SequentialAgentResource):
                sorted_sequential_agents.append(agent)
            elif isinstance(agent, LoopAgentResource):
                sorted_loop_agents.append(agent)
            elif isinstance(agent, ParallelAgentResource):
                sorted_parallel_agents.append(agent)

        return {
            "llm_agents": sorted_llm_agents,
            "sequential_agents": sorted_sequential_agents,
            "loop_agents": sorted_loop_agents,
            "parallel_agents": sorted_parallel_agents,
            "all_agents_sorted": [all_agents[name] for name in sorted_agents],
        }

    def generate_code(
        self, manifest: ParsedManifest, output_dir: str, **_kwargs: Any
    ) -> Dict[str, str]:
        """Generate Google ADK code from parsed manifest."""
        os.makedirs(output_dir, exist_ok=True)

        # Find root agent
        parser = ManifestParser()
        root_agents = parser.find_root_agents(manifest)
        root_agent_name = root_agents[0]  # Use first root agent
        print(f"Identified '{root_agent_name}' as the root agent.")

        generated_files = {}

        # Generate tools.py
        tools_template = self.env.get_template("tools.py.j2")
        tools_content = tools_template.render(tools=manifest.tools)
        tools_path = os.path.join(output_dir, "tools.py")
        with open(tools_path, "w", encoding="utf-8") as f:
            f.write(tools_content)
        generated_files[tools_path] = tools_content
        print(f"Generated {tools_path}")

        # Sort agents topologically to handle dependencies
        sorted_agents = self._topological_sort_agents(manifest)

        # Generate agent.py
        agent_template = self.env.get_template("agent.py.j2")
        agent_content = agent_template.render(
            tools=manifest.tools,
            models=manifest.models,
            llm_agents=sorted_agents["llm_agents"],
            sequential_agents=sorted_agents["sequential_agents"],
            loop_agents=sorted_agents["loop_agents"],
            parallel_agents=sorted_agents["parallel_agents"],
            all_agents_sorted=sorted_agents["all_agents_sorted"],
            root_agent_name=root_agent_name,
        )
        agent_path = os.path.join(output_dir, "agent.py")
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(agent_content)
        generated_files[agent_path] = agent_content
        print(f"Generated {agent_path}")

        # Generate main.py
        main_template = self.env.get_template("main.py.j2")
        main_content = main_template.render()
        main_path = os.path.join(output_dir, "main.py")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(main_content)
        generated_files[main_path] = main_content
        print(f"Generated {main_path}")

        # Create __init__.py
        init_path = os.path.join(output_dir, "__init__.py")
        init_content = "# Auto-generated __init__.py"
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(init_content)
        generated_files[init_path] = init_content
        print(f"Generated {init_path}")

        return generated_files

    def get_required_dependencies(self) -> List[str]:
        """Get required dependencies for Google ADK."""
        return [
            "google-adk>=1.10.0",
        ]

    def validate_manifest_for_provider(self, manifest: ParsedManifest) -> List[str]:
        """Validate manifest for Google ADK specific requirements."""
        errors = []

        # Check that all models use Google provider
        for model in manifest.models:
            if model.spec.provider != "google":
                errors.append(
                    f"Model '{model.metadata.name}' uses provider "
                    f"'{model.spec.provider}', but Google ADK only supports 'google' provider"
                )

        # Check for Google-specific model IDs
        google_model_prefixes = ["gemini", "text", "chat"]
        for model in manifest.models:
            if not any(model.spec.modelId.startswith(prefix) for prefix in google_model_prefixes):
                errors.append(
                    f"Model '{model.metadata.name}' has modelId "
                    f"'{model.spec.modelId}' which doesn't appear to be a Google model"
                )

        return errors
