"""
Unit tests for Google ADK provider generator.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from konductor.core.models import (
    LlmAgentResource,
    ModelResource,
    ParsedManifest,
    SequentialAgentResource,
    ToolResource,
)
from konductor.providers.google_adk.generator import GoogleAdkGenerator


class TestGoogleAdkGenerator:
    """Test the GoogleAdkGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = GoogleAdkGenerator()

    def test_generator_initialization(self):
        """Test generator initialization."""
        assert self.generator.provider_name == "google_adk"
        assert self.generator.templates_dir.endswith("templates")
        assert self.generator.env is not None

    def test_get_required_dependencies(self):
        """Test getting required dependencies."""
        deps = self.generator.get_required_dependencies()
        assert "google-adk>=1.10.0" in deps

    def create_test_manifest(self):
        """Create a test manifest for generation."""
        tool_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "Tool",
            "metadata": {"name": "test-tool"},
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
            "metadata": {"name": "test-model"},
            "spec": {
                "provider": "google",
                "modelId": "gemini-2.5-flash",
                "parameters": {"temperature": 0.7},
            },
        }

        agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmAgent",
            "metadata": {"name": "test-agent"},
            "spec": {
                "modelRef": "test-model",
                "instruction": "You are a test agent",
                "toolRefs": ["test-tool"],
            },
        }

        return ParsedManifest(
            tools=[ToolResource(**tool_data)],
            models=[ModelResource(**model_data)],
            llm_agents=[LlmAgentResource(**agent_data)],
        )

    def test_generate_code_creates_files(self):
        """Test that code generation creates expected files."""
        manifest = self.create_test_manifest()

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)

            # Check that all expected files are created
            expected_files = ["tools.py", "agent.py", "main.py", "__init__.py"]
            for expected_file in expected_files:
                file_path = os.path.join(temp_dir, expected_file)
                assert os.path.exists(file_path), f"File {expected_file} was not created"
                assert file_path in generated_files

            # Check that files have content
            for file_path in generated_files:
                with open(file_path, "r") as f:
                    content = f.read()
                    assert len(content) > 0, f"File {file_path} is empty"

    def test_generate_tools_py_content(self):
        """Test the content of generated tools.py file."""
        manifest = self.create_test_manifest()

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)
            tools_path = os.path.join(temp_dir, "tools.py")

            with open(tools_path, "r") as f:
                content = f.read()

            # Check for expected imports
            assert "from tools.test import test_function" in content
            assert "auto-generated" in content

    def test_generate_agent_py_content(self):
        """Test the content of generated agent.py file."""
        manifest = self.create_test_manifest()

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)
            agent_path = os.path.join(temp_dir, "agent.py")

            with open(agent_path, "r") as f:
                content = f.read()

            # Check for expected content
            assert "from google.adk.agents import LlmAgent" in content
            assert "MODEL_CONFIG_MAP" in content
            assert "TOOL_FUNCTION_MAP" in content
            assert "test-model" in content
            assert "gemini-2.5-flash" in content
            assert "test-agent" in content
            assert "You are a test agent" in content
            assert "root_agent" in content

    def test_generate_main_py_content(self):
        """Test the content of generated main.py file."""
        manifest = self.create_test_manifest()

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)
            main_path = os.path.join(temp_dir, "main.py")

            with open(main_path, "r") as f:
                content = f.read()

            # Check for expected content
            assert "from google.adk.runners import Runner" in content
            assert "from .agent import root_agent" in content
            assert "async def main():" in content
            assert "generated-konductor-app" in content

    def test_generate_with_sequential_agent(self):
        """Test code generation with sequential agent."""
        manifest = self.create_test_manifest()

        # Add a sequential agent
        seq_agent_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "SequentialAgent",
            "metadata": {"name": "test-sequential"},
            "spec": {"subAgentRefs": ["test-agent"]},
        }
        manifest.sequential_agents = [SequentialAgentResource(**seq_agent_data)]

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)
            agent_path = os.path.join(temp_dir, "agent.py")

            with open(agent_path, "r") as f:
                content = f.read()

            # Check for sequential agent content
            assert "SequentialAgent" in content
            assert "test-sequential" in content
            assert "sub_agents" in content

    def test_generate_with_model_parameters(self):
        """Test code generation with model parameters."""
        manifest = self.create_test_manifest()

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)
            agent_path = os.path.join(temp_dir, "agent.py")

            with open(agent_path, "r") as f:
                content = f.read()

            # Check for model parameters
            assert "GenerateContentConfig" in content
            assert "temperature=0.7" in content

    def test_generate_without_tools(self):
        """Test code generation without tools."""
        manifest = ParsedManifest(
            models=[
                ModelResource(
                    **{
                        "apiVersion": "adk.google.com/v1alpha1",
                        "kind": "LlmModel",
                        "metadata": {"name": "test-model"},
                        "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
                    }
                )
            ],
            llm_agents=[
                LlmAgentResource(
                    **{
                        "apiVersion": "adk.google.com/v1alpha1",
                        "kind": "LlmAgent",
                        "metadata": {"name": "test-agent"},
                        "spec": {
                            "modelRef": "test-model",
                            "instruction": "You are a test agent",
                            # No toolRefs
                        },
                    }
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            generated_files = self.generator.generate_code(manifest, temp_dir)

            # Should still generate all files
            assert len(generated_files) == 4

            tools_path = os.path.join(temp_dir, "tools.py")
            with open(tools_path, "r") as f:
                content = f.read()

            # tools.py should be minimal but valid
            assert "auto-generated" in content


class TestGoogleAdkValidation:
    """Test Google ADK specific validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = GoogleAdkGenerator()

    def test_validate_google_provider(self):
        """Test validation passes for Google provider."""
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test-model"},
            "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
        }

        manifest = ParsedManifest(models=[ModelResource(**model_data)])
        errors = self.generator.validate_manifest_for_provider(manifest)
        assert len(errors) == 0

    def test_validate_non_google_provider(self):
        """Test validation fails for non-Google provider."""
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test-model"},
            "spec": {"provider": "openai", "modelId": "gpt-4"},
        }

        manifest = ParsedManifest(models=[ModelResource(**model_data)])
        errors = self.generator.validate_manifest_for_provider(manifest)
        assert len(errors) == 2  # Both provider and model ID errors
        assert any("only supports 'google' provider" in error for error in errors)
        assert any("doesn't appear to be a Google model" in error for error in errors)

    def test_validate_google_model_id(self):
        """Test validation of Google model IDs."""
        # Valid Google model
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test-model"},
            "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
        }

        manifest = ParsedManifest(models=[ModelResource(**model_data)])
        errors = self.generator.validate_manifest_for_provider(manifest)
        assert len(errors) == 0

    def test_validate_non_google_model_id(self):
        """Test validation warning for non-Google model IDs."""
        model_data = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "test-model"},
            "spec": {"provider": "google", "modelId": "unknown-model"},
        }

        manifest = ParsedManifest(models=[ModelResource(**model_data)])
        errors = self.generator.validate_manifest_for_provider(manifest)
        assert len(errors) == 1
        assert "doesn't appear to be a Google model" in errors[0]

    def test_validate_multiple_models_mixed(self):
        """Test validation with mix of valid and invalid models."""
        valid_model = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "valid-model"},
            "spec": {"provider": "google", "modelId": "gemini-2.5-flash"},
        }

        invalid_model = {
            "apiVersion": "adk.google.com/v1alpha1",
            "kind": "LlmModel",
            "metadata": {"name": "invalid-model"},
            "spec": {"provider": "openai", "modelId": "gpt-4"},
        }

        manifest = ParsedManifest(
            models=[ModelResource(**valid_model), ModelResource(**invalid_model)]
        )
        errors = self.generator.validate_manifest_for_provider(manifest)
        assert len(errors) == 2  # Two errors for the invalid model
        error_text = " ".join(errors)
        assert "invalid-model" in error_text
        assert "only supports 'google' provider" in error_text
