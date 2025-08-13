"""
Provider-agnostic manifest parser for Konductor.
"""

from typing import List, Type

import yaml

from .models import (
    RESOURCE_REGISTRY,
    LlmAgentResource,
    LoopAgentResource,
    ModelResource,
    ParallelAgentResource,
    ParsedManifest,
    Resource,
    SequentialAgentResource,
    ToolResource,
)


class ManifestParser:
    """Parses YAML manifests into structured resources."""

    def __init__(self) -> None:
        self.resource_registry = RESOURCE_REGISTRY.copy()

    def register_resource_type(self, kind: str, resource_class: Type[Resource]) -> None:
        """Register a new resource type for parsing."""
        self.resource_registry[kind] = resource_class

    def parse_manifest(self, file_path: str) -> ParsedManifest:
        """Parse a YAML manifest file into structured resources."""
        tools = []
        models = []
        llm_agents = []
        sequential_agents = []
        loop_agents = []
        parallel_agents = []

        with open(file_path, "r", encoding="utf-8") as f:
            docs = yaml.safe_load_all(f)
            for doc in docs:
                if not doc:
                    continue

                kind = doc.get("kind")
                if kind not in self.resource_registry:
                    print(f"Warning: Unknown kind '{kind}' found in manifest. Skipping.")
                    continue

                resource_class = self.resource_registry[kind]
                resource = resource_class(**doc)

                # Categorize resources
                if isinstance(resource, ToolResource):
                    tools.append(resource)
                elif isinstance(resource, ModelResource):
                    models.append(resource)
                elif isinstance(resource, LlmAgentResource):
                    llm_agents.append(resource)
                elif isinstance(resource, SequentialAgentResource):
                    sequential_agents.append(resource)
                elif isinstance(resource, LoopAgentResource):
                    loop_agents.append(resource)
                elif isinstance(resource, ParallelAgentResource):
                    parallel_agents.append(resource)

        manifest = ParsedManifest(
            tools=tools,
            models=models,
            llm_agents=llm_agents,
            sequential_agents=sequential_agents,
            loop_agents=loop_agents,
            parallel_agents=parallel_agents,
        )

        print(
            f"Parsed {len(tools)} tool(s), {len(models)} model(s), "
            f"{len(llm_agents)} LlmAgent(s), {len(sequential_agents)} SequentialAgent(s), "
            f"{len(loop_agents)} LoopAgent(s), {len(parallel_agents)} ParallelAgent(s)."
        )

        return manifest

    def validate_manifest(self, manifest: ParsedManifest) -> List[str]:
        """Validate the parsed manifest for consistency."""
        errors = []

        # Check that all referenced models exist
        model_names = {model.metadata.name for model in manifest.models}
        for agent in manifest.llm_agents:
            if agent.spec.modelRef not in model_names:
                errors.append(
                    f"LlmAgent '{agent.metadata.name}' references unknown model "
                    f"'{agent.spec.modelRef}'"
                )

        # Check that all referenced tools exist
        tool_names = {tool.metadata.name for tool in manifest.tools}
        for agent in manifest.llm_agents:
            if agent.spec.toolRefs:
                for tool_ref in agent.spec.toolRefs:
                    if tool_ref not in tool_names:
                        errors.append(
                            f"LlmAgent '{agent.metadata.name}' references unknown tool '{tool_ref}'"
                        )

        # Check that all referenced sub-agents exist
        agent_names = {agent.metadata.name for agent in manifest.get_all_agents()}

        # Validate SequentialAgent references
        for seq_agent in manifest.sequential_agents:
            for sub_agent_ref in seq_agent.spec.subAgentRefs:
                if sub_agent_ref not in agent_names:
                    errors.append(
                        f"SequentialAgent '{seq_agent.metadata.name}' references "
                        f"unknown sub-agent '{sub_agent_ref}'"
                    )

        # Validate LoopAgent references
        for loop_agent in manifest.loop_agents:
            for sub_agent_ref in loop_agent.spec.subAgentRefs:
                if sub_agent_ref not in agent_names:
                    errors.append(
                        f"LoopAgent '{loop_agent.metadata.name}' references "
                        f"unknown sub-agent '{sub_agent_ref}'"
                    )

        # Validate ParallelAgent references
        for parallel_agent in manifest.parallel_agents:
            for sub_agent_ref in parallel_agent.spec.subAgentRefs:
                if sub_agent_ref not in agent_names:
                    errors.append(
                        f"ParallelAgent '{parallel_agent.metadata.name}' references "
                        f"unknown sub-agent '{sub_agent_ref}'"
                    )

        return errors

    def find_root_agents(self, manifest: ParsedManifest) -> List[str]:
        """Find agents that are not referenced by any workflow agent (potential root agents)."""
        all_sub_agent_refs = set()

        # Collect sub-agent references from all workflow agents
        for seq_agent in manifest.sequential_agents:
            all_sub_agent_refs.update(seq_agent.spec.subAgentRefs)
        for loop_agent in manifest.loop_agents:
            all_sub_agent_refs.update(loop_agent.spec.subAgentRefs)
        for parallel_agent in manifest.parallel_agents:
            all_sub_agent_refs.update(parallel_agent.spec.subAgentRefs)

        root_agents = [
            agent.metadata.name
            for agent in manifest.get_all_agents()
            if agent.metadata.name not in all_sub_agent_refs
        ]

        if not root_agents:
            raise ValueError("Could not determine a root agent. Check for circular dependencies.")

        return root_agents
