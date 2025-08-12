"""
Unit tests for core models.
"""

import pytest
from pydantic import ValidationError

from konductor.core.models import (
    RESOURCE_REGISTRY,
    LlmAgentResource,
    Metadata,
    ModelResource,
    ParsedManifest,
    SequentialAgentResource,
    ToolResource,
)


class TestMetadata:
    """Test the Metadata model."""

    def test_metadata_creation(self):
        """Test basic metadata creation."""
        metadata = Metadata(name="test-resource")
        assert metadata.name == "test-resource"
        assert metadata.labels == {}
        assert metadata.annotations == {}

    def test_metadata_with_labels_and_annotations(self):
        """Test metadata with labels and annotations."""
        metadata = Metadata(
            name="test-resource",
            labels={"env": "test", "version": "1.0"},
            annotations={"description": "A test resource"},
        )
        assert metadata.name == "test-resource"
        assert metadata.labels == {"env": "test", "version": "1.0"}
        assert metadata.annotations == {"description": "A test resource"}


class TestToolResource:
    """Test the ToolResource model."""

    def test_valid_tool_resource(self):
        """Test creating a valid tool resource."""
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

        tool = ToolResource(**tool_data)
        assert tool.metadata.name == "test_tool"
        assert tool.spec.description == "A test tool"
        assert tool.spec.source.file == "tools/test.py"
        assert tool.spec.source.functionName == "test_function"
        assert len(tool.spec.parameters) == 1
        assert tool.spec.parameters[0].name == "input"

    def test_tool_parameter_defaults(self):
        """Test tool parameter defaults."""
        tool_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "Tool",
            "metadata": {"name": "test_tool"},
            "spec": {
                "type": "pythonFunction",
                "description": "A test tool",
                "source": {"file": "tools/test.py", "functionName": "test_function"},
                "parameters": [
                    {
                        "name": "input",
                        "type": "string",
                        "description": "Test input",
                        # required defaults to True
                    }
                ],
            },
        }

        tool = ToolResource(**tool_data)
        assert tool.spec.parameters[0].required is True


class TestModelResource:
    """Test the ModelResource model."""

    def test_valid_model_resource(self):
        """Test creating a valid model resource."""
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test_model"},
            "spec": {
                "provider": "google",
                "modelId": "gemini-2.5-flash",
                "parameters": {"temperature": 0.7, "top_k": 40},
            },
        }

        model = ModelResource(**model_data)
        assert model.metadata.name == "test_model"
        assert model.spec.provider == "google"
        assert model.spec.modelId == "gemini-2.5-flash"
        assert model.spec.parameters["temperature"] == 0.7
        assert model.spec.parameters["top_k"] == 40

    def test_model_without_parameters(self):
        """Test model without parameters."""
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test_model"},
            "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
        }

        model = ModelResource(**model_data)
        assert model.spec.parameters is None


class TestLlmAgentResource:
    """Test the LlmAgentResource model."""

    def test_valid_llm_agent_resource(self):
        """Test creating a valid LLM agent resource."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test_agent"},
            "spec": {
                "modelRef": "test_model",
                "instruction": "You are a test agent",
                "toolRefs": ["tool1", "tool2"],
                "output_key": "result",
            },
        }

        agent = LlmAgentResource(**agent_data)
        assert agent.metadata.name == "test_agent"
        assert agent.spec.modelRef == "test_model"
        assert agent.spec.instruction == "You are a test agent"
        assert agent.spec.toolRefs == ["tool1", "tool2"]
        assert agent.spec.output_key == "result"

    def test_llm_agent_with_defaults(self):
        """Test LLM agent with default values."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test_agent"},
            "spec": {
                "modelRef": "test_model",
                "instruction": "You are a test agent",
                # toolRefs and output_key are optional
            },
        }

        agent = LlmAgentResource(**agent_data)
        assert agent.spec.toolRefs == []
        assert agent.spec.output_key is None

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test_agent"},
            "spec": {
                "instruction": "You are a test agent"
                # Missing modelRef
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            LlmAgentResource(**agent_data)
        assert "modelRef" in str(exc_info.value)


class TestSequentialAgentResource:
    """Test the SequentialAgentResource model."""

    def test_valid_sequential_agent_resource(self):
        """Test creating a valid sequential agent resource."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "test_sequential"},
            "spec": {"subAgentRefs": ["test_agent"], "toolRefs": ["tool1"]},
        }

        agent = SequentialAgentResource(**agent_data)
        assert agent.metadata.name == "test_sequential"
        assert agent.spec.subAgentRefs == ["test_agent"]
        assert agent.spec.toolRefs == ["tool1"]

    def test_sequential_agent_with_defaults(self):
        """Test sequential agent with default values."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "test_sequential"},
            "spec": {
                "subAgentRefs": ["test_agent"]
                # toolRefs is optional
            },
        }

        agent = SequentialAgentResource(**agent_data)
        assert agent.spec.toolRefs == []

    def test_missing_sub_agent_refs(self):
        """Test validation error for missing subAgentRefs."""
        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "test_sequential"},
            "spec": {
                # Missing subAgentRefs
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            SequentialAgentResource(**agent_data)
        assert "subAgentRefs" in str(exc_info.value)


class TestParsedManifest:
    """Test the ParsedManifest model."""

    def test_empty_parsed_manifest(self):
        """Test creating an empty parsed manifest."""
        manifest = ParsedManifest()
        assert len(manifest.tools) == 0
        assert len(manifest.models) == 0
        assert len(manifest.llm_agents) == 0
        assert len(manifest.sequential_agents) == 0

    def test_get_all_agents(self):
        """Test getting all agents from manifest."""
        llm_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "llm-agent"},
            "spec": {"modelRef": "model1", "instruction": "Test"},
        }

        seq_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "seq-agent"},
            "spec": {"subAgentRefs": ["llm-agent"]},
        }

        manifest = ParsedManifest(
            llm_agents=[LlmAgentResource(**llm_agent_data)],
            sequential_agents=[SequentialAgentResource(**seq_agent_data)],
        )

        all_agents = manifest.get_all_agents()
        assert len(all_agents) == 2
        assert all_agents[0].metadata.name == "llm-agent"
        assert all_agents[1].metadata.name == "seq-agent"

    def test_find_agent_by_name(self):
        """Test finding agent by name."""
        llm_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test_agent"},
            "spec": {"modelRef": "model1", "instruction": "Test"},
        }

        manifest = ParsedManifest(llm_agents=[LlmAgentResource(**llm_agent_data)])

        found_agent = manifest.find_agent_by_name("test_agent")
        assert found_agent is not None
        assert found_agent.metadata.name == "test_agent"

        not_found = manifest.find_agent_by_name("nonexistent")
        assert not_found is None


class TestResourceRegistry:
    """Test the resource registry."""

    def test_resource_registry_contents(self):
        """Test that all expected resource types are registered."""
        expected_kinds = {"Tool", "Model", "LlmModel", "LlmAgent", "SequentialAgent"}

        assert set(RESOURCE_REGISTRY.keys()) == expected_kinds

        # Test that registry maps to correct classes
        assert RESOURCE_REGISTRY["Tool"] == ToolResource
        assert RESOURCE_REGISTRY["Model"] == ModelResource
        assert RESOURCE_REGISTRY["LlmModel"] == ModelResource  # Backward compatibility
        assert RESOURCE_REGISTRY["LlmAgent"] == LlmAgentResource
        assert RESOURCE_REGISTRY["SequentialAgent"] == SequentialAgentResource
