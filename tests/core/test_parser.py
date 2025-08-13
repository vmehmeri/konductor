"""
Unit tests for core parser functionality.
"""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from konductor.core.models import (
    LlmAgentResource,
    LoopAgentResource,
    ModelResource,
    ParallelAgentResource,
    SequentialAgentResource,
    ToolResource,
)
from konductor.core.parser import ManifestParser
from tests.fixtures.test_manifests import (
    COMPLETE_MANIFEST,
    COMPLETE_MANIFEST_WITH_NEW_AGENTS,
    INVALID_MANIFEST_MISSING_FIELDS,
    INVALID_MANIFEST_UNKNOWN_KIND,
    LOOP_AGENT_MANIFEST,
    PARALLEL_AGENT_MANIFEST,
    SEQUENTIAL_AGENT_MANIFEST,
    SIMPLE_AGENT_ONLY_MANIFEST,
    SIMPLE_MODEL_MANIFEST,
    SIMPLE_TOOL_MANIFEST,
)


class TestManifestParser:
    """Test the ManifestParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ManifestParser()

    def test_parser_initialization(self):
        """Test parser initialization."""
        assert self.parser is not None
        assert "Tool" in self.parser.resource_registry
        assert "LlmAgent" in self.parser.resource_registry

    def test_register_resource_type(self):
        """Test registering a new resource type."""

        class CustomResource:
            pass

        self.parser.register_resource_type("Custom", CustomResource)
        assert self.parser.resource_registry["Custom"] == CustomResource

    def test_parse_simple_tool_manifest(self):
        """Test parsing a simple tool manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(SIMPLE_TOOL_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 1
                assert len(manifest.models) == 0
                assert len(manifest.llm_agents) == 0
                assert len(manifest.sequential_agents) == 0
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 0

                tool = manifest.tools[0]
                assert isinstance(tool, ToolResource)
                assert tool.metadata.name == "test_tool"
                assert tool.spec.description == "A test tool"
                assert tool.spec.source.file == "tools/test.py"
                assert tool.spec.source.functionName == "test_function"
            finally:
                os.unlink(f.name)

    def test_parse_simple_model_manifest(self):
        """Test parsing a simple model manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(SIMPLE_MODEL_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 0
                assert len(manifest.models) == 1
                assert len(manifest.llm_agents) == 0
                assert len(manifest.sequential_agents) == 0
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 0

                model = manifest.models[0]
                assert isinstance(model, ModelResource)
                assert model.metadata.name == "test_model"
                assert model.spec.provider == "google"
                assert model.spec.modelId == "gemini-2.5-flash"
                assert model.spec.parameters["temperature"] == 0.7
            finally:
                os.unlink(f.name)

    def test_parse_simple_agent_manifest(self):
        """Test parsing a simple agent manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(SIMPLE_AGENT_ONLY_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 0
                assert len(manifest.models) == 0
                assert len(manifest.llm_agents) == 1
                assert len(manifest.sequential_agents) == 0
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 0

                agent = manifest.llm_agents[0]
                assert isinstance(agent, LlmAgentResource)
                assert agent.metadata.name == "test_agent"
                assert agent.spec.modelRef == "test_model"
                assert agent.spec.instruction == "You are a test agent"
                assert agent.spec.toolRefs == ["test_tool"]
            finally:
                os.unlink(f.name)

    def test_parse_sequential_agent_manifest(self):
        """Test parsing a sequential agent manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(SEQUENTIAL_AGENT_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 0
                assert len(manifest.models) == 0
                assert len(manifest.llm_agents) == 0
                assert len(manifest.sequential_agents) == 1
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 0

                agent = manifest.sequential_agents[0]
                assert isinstance(agent, SequentialAgentResource)
                assert agent.metadata.name == "test_sequential"
                assert agent.spec.subAgentRefs == ["test_agent"]
            finally:
                os.unlink(f.name)

    def test_parse_loop_agent_manifest(self):
        """Test parsing a loop agent manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(LOOP_AGENT_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 0
                assert len(manifest.models) == 0
                assert len(manifest.llm_agents) == 0
                assert len(manifest.sequential_agents) == 0
                assert len(manifest.loop_agents) == 1
                assert len(manifest.parallel_agents) == 0

                agent = manifest.loop_agents[0]
                assert isinstance(agent, LoopAgentResource)
                assert agent.metadata.name == "test_loop"
                assert agent.spec.subAgentRefs == ["test_agent"]
                assert agent.spec.maxIterations == 5
            finally:
                os.unlink(f.name)

    def test_parse_parallel_agent_manifest(self):
        """Test parsing a parallel agent manifest."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(PARALLEL_AGENT_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 0
                assert len(manifest.models) == 0
                assert len(manifest.llm_agents) == 0
                assert len(manifest.sequential_agents) == 0
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 1

                agent = manifest.parallel_agents[0]
                assert isinstance(agent, ParallelAgentResource)
                assert agent.metadata.name == "test_parallel"
                assert agent.spec.subAgentRefs == ["test_agent1", "test_agent2"]
            finally:
                os.unlink(f.name)

    def test_parse_complete_manifest(self):
        """Test parsing a complete manifest with multiple resources."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(COMPLETE_MANIFEST)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 1
                assert len(manifest.models) == 1
                assert len(manifest.llm_agents) == 1
                assert len(manifest.sequential_agents) == 1
                assert len(manifest.loop_agents) == 0
                assert len(manifest.parallel_agents) == 0

                # Verify each resource type
                assert manifest.tools[0].metadata.name == "test_tool"
                assert manifest.models[0].metadata.name == "test_model"
                assert manifest.llm_agents[0].metadata.name == "test_agent"
                assert manifest.sequential_agents[0].metadata.name == "test_sequential"
            finally:
                os.unlink(f.name)

    def test_parse_complete_manifest_with_new_agents(self):
        """Test parsing a complete manifest with all agent types."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(COMPLETE_MANIFEST_WITH_NEW_AGENTS)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)

                assert len(manifest.tools) == 1
                assert len(manifest.models) == 1
                assert len(manifest.llm_agents) == 1
                assert len(manifest.sequential_agents) == 1
                assert len(manifest.loop_agents) == 1
                assert len(manifest.parallel_agents) == 1

                # Verify each resource type
                assert manifest.tools[0].metadata.name == "test_tool"
                assert manifest.models[0].metadata.name == "test_model"
                assert manifest.llm_agents[0].metadata.name == "test_agent"
                assert manifest.sequential_agents[0].metadata.name == "test_sequential"
                assert manifest.loop_agents[0].metadata.name == "test_loop"
                assert manifest.parallel_agents[0].metadata.name == "test_parallel"
            finally:
                os.unlink(f.name)

    def test_parse_unknown_kind_warning(self):
        """Test that unknown kinds produce warnings but don't fail."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(INVALID_MANIFEST_UNKNOWN_KIND)
            f.flush()

            try:
                with patch("builtins.print") as mock_print:
                    manifest = self.parser.parse_manifest(f.name)

                    # Should produce a warning
                    mock_print.assert_called()
                    print_args = [call.args[0] for call in mock_print.call_args_list]
                    assert any("Unknown kind 'UnknownKind'" in arg for arg in print_args)

                    # Manifest should be empty
                    assert len(manifest.tools) == 0
                    assert len(manifest.models) == 0
                    assert len(manifest.llm_agents) == 0
                    assert len(manifest.sequential_agents) == 0
                    assert len(manifest.loop_agents) == 0
                    assert len(manifest.parallel_agents) == 0
            finally:
                os.unlink(f.name)

    def test_parse_empty_document(self):
        """Test parsing manifest with empty documents."""
        manifest_content = """
---
# Empty document
---
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: test_model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
---
# Another empty document
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(manifest_content)
            f.flush()

            try:
                manifest = self.parser.parse_manifest(f.name)
                assert len(manifest.models) == 1
                assert manifest.models[0].metadata.name == "test_model"
            finally:
                os.unlink(f.name)


class TestManifestValidation:
    """Test manifest validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ManifestParser()

    def create_test_manifest(self):
        """Create a test manifest for validation."""
        tool_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "Tool",
            "metadata": {"name": "test_tool"},
            "spec": {
                "type": "pythonFunction",
                "description": "A test tool",
                "source": {"file": "tools/test.py", "functionName": "test_function"},
                "parameters": [{"name": "input", "type": "string", "description": "Test input"}],
            },
        }

        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test_model"},
            "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
        }

        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test_agent"},
            "spec": {
                "modelRef": "test_model",
                "instruction": "You are a test agent",
                "toolRefs": ["test_tool"],
            },
        }

        seq_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "test_sequential"},
            "spec": {"subAgentRefs": ["test_agent"]},
        }

        from konductor.core.models import ParsedManifest

        return ParsedManifest(
            tools=[ToolResource(**tool_data)],
            models=[ModelResource(**model_data)],
            llm_agents=[LlmAgentResource(**agent_data)],
            sequential_agents=[SequentialAgentResource(**seq_agent_data)],
        )

    def test_validate_valid_manifest(self):
        """Test validation of a valid manifest."""
        manifest = self.create_test_manifest()
        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 0

    def test_validate_missing_model_reference(self):
        """Test validation error for missing model reference."""
        manifest = self.create_test_manifest()
        # Remove the model
        manifest.models = []

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 1
        assert "unknown model 'test_model'" in errors[0]

    def test_validate_missing_tool_reference(self):
        """Test validation error for missing tool reference."""
        manifest = self.create_test_manifest()
        # Remove the tool
        manifest.tools = []

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 1
        assert "unknown tool 'test_tool'" in errors[0]

    def test_validate_missing_sub_agent_reference(self):
        """Test validation error for missing sub-agent reference."""
        manifest = self.create_test_manifest()
        # Remove the LLM agent
        manifest.llm_agents = []

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 1
        assert "unknown sub-agent 'test_agent'" in errors[0]

    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        manifest = self.create_test_manifest()
        # Remove both model and tool
        manifest.models = []
        manifest.tools = []

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 2
        error_text = " ".join(errors)
        assert "unknown model 'test_model'" in error_text
        assert "unknown tool 'test_tool'" in error_text

    def test_validate_loop_agent_references(self):
        """Test validation of LoopAgent references."""
        from konductor.core.models import ParsedManifest

        # Create a loop agent that references non-existent sub-agents
        loop_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LoopAgent",
            "metadata": {"name": "test_loop"},
            "spec": {
                "subAgentRefs": ["nonexistent_agent"],
                "maxIterations": 3,
            },
        }

        manifest = ParsedManifest(
            loop_agents=[LoopAgentResource(**loop_agent_data)],
        )

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 1
        error_text = " ".join(errors)
        assert "unknown sub-agent 'nonexistent_agent'" in error_text

    def test_validate_parallel_agent_references(self):
        """Test validation of ParallelAgent references."""
        from konductor.core.models import ParsedManifest

        # Create a parallel agent that references non-existent sub-agents
        parallel_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "ParallelAgent",
            "metadata": {"name": "test_parallel"},
            "spec": {
                "subAgentRefs": ["nonexistent_agent1", "nonexistent_agent2"],
            },
        }

        manifest = ParsedManifest(
            parallel_agents=[ParallelAgentResource(**parallel_agent_data)],
        )

        errors = self.parser.validate_manifest(manifest)
        assert len(errors) == 2
        error_text = " ".join(errors)
        assert "unknown sub-agent 'nonexistent_agent1'" in error_text
        assert "unknown sub-agent 'nonexistent_agent2'" in error_text


class TestRootAgentIdentification:
    """Test root agent identification functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ManifestParser()

    def test_find_root_agents_single_agent(self):
        """Test finding root agent with single agent."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "root-agent"},
            "spec": {"modelRef": "test_model", "instruction": "You are a root agent"},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(llm_agents=[LlmAgentResource(**agent_data)])

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 1
        assert root_agents[0] == "root-agent"

    def test_find_root_agents_with_sequential(self):
        """Test finding root agent with sequential agent."""
        llm_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "sub-agent"},
            "spec": {"modelRef": "test_model", "instruction": "You are a sub agent"},
        }

        seq_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "root-sequential"},
            "spec": {"subAgentRefs": ["sub-agent"]},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**llm_agent_data)],
            sequential_agents=[SequentialAgentResource(**seq_agent_data)],
        )

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 1
        assert root_agents[0] == "root-sequential"

    def test_find_root_agents_multiple_roots(self):
        """Test finding multiple root agents."""
        agent1_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "root-agent-1"},
            "spec": {"modelRef": "test_model", "instruction": "You are root agent 1"},
        }

        agent2_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "root-agent-2"},
            "spec": {"modelRef": "test_model", "instruction": "You are root agent 2"},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**agent1_data), LlmAgentResource(**agent2_data)]
        )

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 2
        assert set(root_agents) == {"root-agent-1", "root-agent-2"}

    def test_find_root_agents_no_agents(self):
        """Test finding root agents with no agents."""
        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest()

        with pytest.raises(ValueError, match="Could not determine a root agent"):
            self.parser.find_root_agents(manifest)

    def test_find_root_agents_with_loop_agent(self):
        """Test finding root agent with loop agent."""
        llm_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "sub-agent"},
            "spec": {"modelRef": "test_model", "instruction": "You are a sub agent"},
        }

        loop_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LoopAgent",
            "metadata": {"name": "root-loop"},
            "spec": {"subAgentRefs": ["sub-agent"], "maxIterations": 3},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**llm_agent_data)],
            loop_agents=[LoopAgentResource(**loop_agent_data)],
        )

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 1
        assert root_agents[0] == "root-loop"

    def test_find_root_agents_with_parallel_agent(self):
        """Test finding root agent with parallel agent."""
        llm_agent1_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "sub-agent-1"},
            "spec": {"modelRef": "test_model", "instruction": "You are sub agent 1"},
        }

        llm_agent2_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "sub-agent-2"},
            "spec": {"modelRef": "test_model", "instruction": "You are sub agent 2"},
        }

        parallel_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "ParallelAgent",
            "metadata": {"name": "root-parallel"},
            "spec": {"subAgentRefs": ["sub-agent-1", "sub-agent-2"]},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**llm_agent1_data), LlmAgentResource(**llm_agent2_data)],
            parallel_agents=[ParallelAgentResource(**parallel_agent_data)],
        )

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 1
        assert root_agents[0] == "root-parallel"

    def test_find_root_agents_complex_hierarchy(self):
        """Test finding root agent with complex hierarchy involving all agent types."""
        llm_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "base-agent"},
            "spec": {"modelRef": "test_model", "instruction": "You are a base agent"},
        }

        loop_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LoopAgent",
            "metadata": {"name": "loop-processor"},
            "spec": {"subAgentRefs": ["base-agent"], "maxIterations": 3},
        }

        parallel_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "ParallelAgent",
            "metadata": {"name": "parallel-processor"},
            "spec": {"subAgentRefs": ["base-agent"]},
        }

        seq_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "root-orchestrator"},
            "spec": {"subAgentRefs": ["loop-processor", "parallel-processor"]},
        }

        from konductor.core.models import ParsedManifest

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**llm_agent_data)],
            loop_agents=[LoopAgentResource(**loop_agent_data)],
            parallel_agents=[ParallelAgentResource(**parallel_agent_data)],
            sequential_agents=[SequentialAgentResource(**seq_agent_data)],
        )

        root_agents = self.parser.find_root_agents(manifest)
        assert len(root_agents) == 1
        assert root_agents[0] == "root-orchestrator"
