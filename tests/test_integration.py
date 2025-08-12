"""
Integration tests for end-to-end workflows.
"""

import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

import pytest

from konductor.core.generator import KonductorGenerator
from konductor.core.parser import ManifestParser
from tests.fixtures.test_manifests import COMPLETE_MANIFEST


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_complete_workflow_simple_agent(self):
        """Test complete workflow from YAML to generated code."""
        simple_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: test-model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
  parameters:
    temperature: 0.7
---
apiVersion: adk.google.com/v1alpha1
kind: Tool
metadata:
  name: echo-tool
spec:
  type: pythonFunction
  description: A simple echo tool
  source:
    file: "tools/echo.py"
    functionName: "echo_function"
  parameters:
    - name: "message"
      type: "string"
      description: "Message to echo"
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: echo-agent
spec:
  modelRef: test-model
  instruction: "You are an echo agent that repeats messages."
  toolRefs:
    - echo-tool
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(simple_manifest)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                # Test the complete workflow
                generator = KonductorGenerator(provider="google_adk")
                generated_files = generator.generate_from_manifest(manifest_file.name, output_dir)

                # Verify all expected files were generated
                expected_files = ["tools.py", "agent.py", "main.py", "__init__.py"]
                for expected_file in expected_files:
                    file_path = os.path.join(output_dir, expected_file)
                    assert os.path.exists(file_path)
                    assert file_path in generated_files

                # Verify content quality
                agent_path = os.path.join(output_dir, "agent.py")
                with open(agent_path, "r") as f:
                    agent_content = f.read()

                # Check for key components
                assert "test-model" in agent_content
                assert "gemini-2.5-flash" in agent_content
                assert "echo-agent" in agent_content
                assert "echo_function" in agent_content
                assert "You are an echo agent" in agent_content
                assert "root_agent" in agent_content

                tools_path = os.path.join(output_dir, "tools.py")
                with open(tools_path, "r") as f:
                    tools_content = f.read()

                assert "from tools.echo import echo_function" in tools_content

                main_path = os.path.join(output_dir, "main.py")
                with open(main_path, "r") as f:
                    main_content = f.read()

                assert "from .agent import root_agent" in main_content
                assert "async def main():" in main_content

        os.unlink(manifest_file.name)

    def test_complete_workflow_sequential_agent(self):
        """Test complete workflow with sequential agent."""
        sequential_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: creative-model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
  parameters:
    temperature: 0.8
---
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: focused-model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
  parameters:
    temperature: 0.2
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: idea-generator
spec:
  modelRef: creative-model
  instruction: "Generate creative ideas."
  output_key: "ideas"
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: idea-refiner
spec:
  modelRef: focused-model
  instruction: "Refine the ideas: {ideas}"
---
apiVersion: adk.google.com/v1alpha1
kind: SequentialAgent
metadata:
  name: pipeline
spec:
  subAgentRefs:
    - idea-generator
    - idea-refiner
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(sequential_manifest)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                generator = KonductorGenerator(provider="google_adk")
                generated_files = generator.generate_from_manifest(manifest_file.name, output_dir)

                # Verify generation succeeded
                assert len(generated_files) == 4

                agent_path = os.path.join(output_dir, "agent.py")
                with open(agent_path, "r") as f:
                    agent_content = f.read()

                # Check for sequential agent components
                assert "SequentialAgent" in agent_content
                assert "pipeline" in agent_content
                assert "idea-generator" in agent_content
                assert "idea-refiner" in agent_content
                assert "sub_agents" in agent_content
                assert "temperature=0.8" in agent_content
                assert "temperature=0.2" in agent_content
                assert 'output_key="ideas"' in agent_content

        os.unlink(manifest_file.name)

    @pytest.mark.slow
    def test_cli_integration_with_real_examples(self):
        """Test CLI integration with real example files."""
        # Test with the actual example files
        simple_example = "examples/simple_agent_stack.yaml"
        sequential_example = "examples/sequential_stack.yaml"

        if not os.path.exists(simple_example):
            pytest.skip("Example files not found")

        with tempfile.TemporaryDirectory() as output_dir:
            # Test simple agent example
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "konductor.cli",
                    "generate",
                    simple_example,
                    "-o",
                    os.path.join(output_dir, "simple"),
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, f"CLI failed: {result.stderr}"
            assert os.path.exists(os.path.join(output_dir, "simple", "agent.py"))
            assert os.path.exists(os.path.join(output_dir, "simple", "tools.py"))

            # Test sequential agent example
            if os.path.exists(sequential_example):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "konductor.cli",
                        "generate",
                        sequential_example,
                        "-o",
                        os.path.join(output_dir, "sequential"),
                    ],
                    capture_output=True,
                    text=True,
                )

                assert result.returncode == 0, f"CLI failed: {result.stderr}"
                assert os.path.exists(os.path.join(output_dir, "sequential", "agent.py"))

    def test_validation_error_handling(self):
        """Test proper error handling for validation failures."""
        invalid_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: invalid-agent
spec:
  modelRef: nonexistent-model
  instruction: "This agent references a model that doesn't exist."
  toolRefs:
    - nonexistent-tool
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(invalid_manifest)
            manifest_file.flush()

            generator = KonductorGenerator(provider="google_adk")

            with pytest.raises(ValueError) as exc_info:
                generator.generate_from_manifest(manifest_file.name, "output")

            error_message = str(exc_info.value)
            assert "validation failed" in error_message.lower()
            assert "nonexistent-model" in error_message
            assert "nonexistent-tool" in error_message

        os.unlink(manifest_file.name)

    def test_provider_validation_error_handling(self):
        """Test provider-specific validation error handling."""
        invalid_provider_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: invalid-model
spec:
  provider: openai
  modelId: "gpt-4"
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: test-agent
spec:
  modelRef: invalid-model
  instruction: "This uses an unsupported provider."
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(invalid_provider_manifest)
            manifest_file.flush()

            generator = KonductorGenerator(provider="google_adk")

            with pytest.raises(ValueError) as exc_info:
                generator.generate_from_manifest(manifest_file.name, "output")

            error_message = str(exc_info.value)
            assert "provider validation failed" in error_message.lower()
            assert "only supports 'google' provider" in error_message

        os.unlink(manifest_file.name)


class TestProviderSystem:
    """Test the provider system integration."""

    def test_provider_registry_integration(self):
        """Test that provider registry works correctly."""
        generator = KonductorGenerator()

        # Test default provider
        assert generator.provider_name == "google_adk"
        assert generator.provider is not None

        # Test listing providers
        providers = generator.list_available_providers()
        assert "google_adk" in providers

        # Test dependencies
        deps_info = generator.get_required_dependencies()
        assert deps_info["provider"] == "google_adk"
        assert "google-adk" in str(deps_info["dependencies"])

    def test_unknown_provider_error(self):
        """Test error handling for unknown provider."""
        generator = KonductorGenerator(provider="unknown_provider")
        # Error should be raised when trying to access the provider
        with pytest.raises(ValueError, match="Unknown provider"):
            _ = generator.provider


class TestFileGeneration:
    """Test file generation quality and correctness."""

    def test_generated_python_syntax(self):
        """Test that generated Python files have valid syntax."""
        test_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: syntax-test-model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: syntax-test-agent
spec:
  modelRef: syntax-test-model
  instruction: "Test agent for syntax validation."
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(test_manifest)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                generator = KonductorGenerator(provider="google_adk")
                generated_files = generator.generate_from_manifest(manifest_file.name, output_dir)

                # Test that all generated Python files have valid syntax
                python_files = [f for f in generated_files if f.endswith(".py")]

                for py_file in python_files:
                    with open(py_file, "r") as f:
                        content = f.read()

                    # Try to compile the Python code
                    try:
                        compile(content, py_file, "exec")
                    except SyntaxError as e:
                        pytest.fail(f"Generated file {py_file} has syntax error: {e}")

        os.unlink(manifest_file.name)

    def test_generated_imports_validity(self):
        """Test that generated imports are valid."""
        test_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmModel
metadata:
  name: import-test-model
spec:
  provider: google
  modelId: "gemini-2.5-flash"
---
apiVersion: adk.google.com/v1alpha1
kind: Tool
metadata:
  name: import-test-tool
spec:
  type: pythonFunction
  description: A test tool
  source:
    file: "some/nested/path/tool.py"
    functionName: "test_function"
  parameters:
    - name: "input"
      type: "string"
      description: "Test input"
---
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: import-test-agent
spec:
  modelRef: import-test-model
  instruction: "Test agent for import validation."
  toolRefs:
    - import-test-tool
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(test_manifest)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                generator = KonductorGenerator(provider="google_adk")
                generated_files = generator.generate_from_manifest(manifest_file.name, output_dir)

                # Check tools.py for proper import generation
                tools_path = os.path.join(output_dir, "tools.py")
                with open(tools_path, "r") as f:
                    tools_content = f.read()

                # Should convert file path to proper Python import
                assert "from some.nested.path.tool import test_function" in tools_content

        os.unlink(manifest_file.name)
