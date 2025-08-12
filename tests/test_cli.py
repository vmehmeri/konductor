"""
Unit tests for CLI interface.
"""

import os
import sys
import tempfile
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from konductor.cli import main
from tests.fixtures.test_manifests import SIMPLE_AGENT_MANIFEST


class TestCLIGenerate:
    """Test the CLI generate command."""

    def test_generate_command_success(self):
        """Test successful generate command."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(SIMPLE_AGENT_MANIFEST)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                test_args = ["konductor", "generate", manifest_file.name, "-o", output_dir]

                with patch.object(sys, "argv", test_args):
                    main()  # Should not raise SystemExit on success

                    # Check that files were generated
                    assert os.path.exists(os.path.join(output_dir, "agent.py"))
                    assert os.path.exists(os.path.join(output_dir, "tools.py"))
                    assert os.path.exists(os.path.join(output_dir, "main.py"))
                    assert os.path.exists(os.path.join(output_dir, "__init__.py"))

            os.unlink(manifest_file.name)

    def test_generate_command_with_provider(self):
        """Test generate command with specific provider."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(SIMPLE_AGENT_MANIFEST)
            manifest_file.flush()

            with tempfile.TemporaryDirectory() as output_dir:
                test_args = [
                    "konductor",
                    "generate",
                    manifest_file.name,
                    "-p",
                    "google_adk",
                    "-o",
                    output_dir,
                ]

                with patch.object(sys, "argv", test_args):
                    main()  # Should not raise SystemExit on success

                    # Check that files were generated
                    assert os.path.exists(os.path.join(output_dir, "agent.py"))

            os.unlink(manifest_file.name)

    def test_generate_command_missing_file(self):
        """Test generate command with missing manifest file."""
        test_args = ["konductor", "generate", "nonexistent_file.yaml"]

        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit with error code
                assert exc_info.value.code == 1

                # Should print error message
                mock_print.assert_called()
                print_args = [str(call.args[0]) for call in mock_print.call_args_list]
                assert any("not found" in arg for arg in print_args)

    def test_generate_command_invalid_manifest(self):
        """Test generate command with invalid manifest."""
        invalid_manifest = """
apiVersion: adk.google.com/v1alpha1
kind: LlmAgent
metadata:
  name: invalid-agent
spec:
  instruction: "Missing required modelRef field"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(invalid_manifest)
            manifest_file.flush()

            test_args = ["konductor", "generate", manifest_file.name]

            with patch.object(sys, "argv", test_args):
                with patch("builtins.print") as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    # Should exit with error code
                    assert exc_info.value.code == 1

                    # Should print error message
                    mock_print.assert_called()
                    print_args = [str(call.args[0]) for call in mock_print.call_args_list]
                    assert any("Error:" in arg for arg in print_args)

            os.unlink(manifest_file.name)


class TestCLIListProviders:
    """Test the CLI list-providers command."""

    def test_list_providers_command(self):
        """Test list-providers command."""
        test_args = ["konductor", "list-providers"]

        captured_output = StringIO()
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", captured_output):
                try:
                    main()
                except SystemExit as e:
                    assert e.code is None or e.code == 0

        output = captured_output.getvalue()
        assert "Available providers:" in output
        assert "google_adk" in output


class TestCLIDependencies:
    """Test the CLI dependencies command."""

    def test_dependencies_command_default(self):
        """Test dependencies command with default provider."""
        test_args = ["konductor", "dependencies"]

        captured_output = StringIO()
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", captured_output):
                try:
                    main()
                except SystemExit as e:
                    assert e.code is None or e.code == 0

        output = captured_output.getvalue()
        assert "Dependencies for provider 'google_adk':" in output
        assert "google-adk" in output

    def test_dependencies_command_specific_provider(self):
        """Test dependencies command with specific provider."""
        test_args = ["konductor", "dependencies", "-p", "google_adk"]

        captured_output = StringIO()
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", captured_output):
                try:
                    main()
                except SystemExit as e:
                    assert e.code is None or e.code == 0

        output = captured_output.getvalue()
        assert "Dependencies for provider 'google_adk':" in output
        assert "google-adk" in output


class TestCLIHelp:
    """Test CLI help and error handling."""

    def test_no_command_shows_help(self):
        """Test that running without command shows help."""
        test_args = ["konductor"]

        captured_output = StringIO()
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", captured_output):
                main()  # Should not exit, just show help

        output = captured_output.getvalue()
        assert "usage:" in output.lower() or "konductor" in output

    def test_generate_help(self):
        """Test generate command help."""
        test_args = ["konductor", "generate", "-h"]

        captured_output = StringIO()
        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", captured_output):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Help should exit with code 0
                assert exc_info.value.code == 0

        output = captured_output.getvalue()
        assert "manifest_file" in output
        assert "--provider" in output or "-p" in output
        assert "--output-dir" in output or "-o" in output

    def test_unknown_provider_error(self):
        """Test error handling for unknown provider."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(SIMPLE_AGENT_MANIFEST)
            manifest_file.flush()

            test_args = ["konductor", "generate", manifest_file.name, "-p", "unknown_provider"]

            with patch.object(sys, "argv", test_args):
                with patch("builtins.print") as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    # Should exit with error code
                    assert exc_info.value.code == 1

                    # Should print error message
                    mock_print.assert_called()
                    print_args = [str(call.args[0]) for call in mock_print.call_args_list]
                    assert any("Error:" in arg for arg in print_args)

            os.unlink(manifest_file.name)


class TestCLIArguments:
    """Test CLI argument parsing and validation."""

    def test_generate_default_arguments(self):
        """Test generate command with default arguments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(SIMPLE_AGENT_MANIFEST)
            manifest_file.flush()

            test_args = ["konductor", "generate", manifest_file.name]

            with patch.object(sys, "argv", test_args):
                with patch("konductor.cli.KonductorGenerator") as mock_generator_class:
                    mock_generator = MagicMock()
                    mock_generator_class.return_value = mock_generator
                    mock_generator.generate_from_manifest.return_value = {}

                    main()  # Should not raise SystemExit on success

                    # Should use default provider and output directory
                    mock_generator_class.assert_called_with(provider="google_adk")
                    mock_generator.generate_from_manifest.assert_called_once()
                    # Check the actual call
                    call_args = mock_generator.generate_from_manifest.call_args
                    assert call_args[0][0] == manifest_file.name  # First positional arg
                    assert call_args[0][1] == "generated_agent"  # Second positional arg

            os.unlink(manifest_file.name)

    def test_generate_custom_arguments(self):
        """Test generate command with custom arguments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as manifest_file:
            manifest_file.write(SIMPLE_AGENT_MANIFEST)
            manifest_file.flush()

            test_args = [
                "konductor",
                "generate",
                manifest_file.name,
                "-p",
                "google_adk",
                "-o",
                "custom_output",
            ]

            with patch.object(sys, "argv", test_args):
                with patch("konductor.cli.KonductorGenerator") as mock_generator_class:
                    mock_generator = MagicMock()
                    mock_generator_class.return_value = mock_generator
                    mock_generator.generate_from_manifest.return_value = {}

                    main()  # Should not raise SystemExit on success

                    # Should use custom provider and output directory
                    mock_generator_class.assert_called_with(provider="google_adk")
                    mock_generator.generate_from_manifest.assert_called_once()
                    # Check the actual call
                    call_args = mock_generator.generate_from_manifest.call_args
                    assert call_args[0][0] == manifest_file.name  # First positional arg
                    assert call_args[0][1] == "custom_output"  # Second positional arg

            os.unlink(manifest_file.name)
