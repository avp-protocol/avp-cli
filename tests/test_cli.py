"""Tests for AVP CLI."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from avp_cli.main import cli


class TestCLI:
    """Test suite for AVP CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield str(Path(tmpdir) / "test_vault.enc")

    def test_version(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help(self, runner):
        """Test help output."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Agent Vault Protocol CLI" in result.output

    def test_init_vault(self, runner, temp_vault):
        """Test vault initialization."""
        result = runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "Vault initialized" in result.output
        assert Path(temp_vault).exists()

    def test_store_and_get(self, runner, temp_vault):
        """Test storing and retrieving credentials."""
        # Initialize vault
        runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # Store credential
        result = runner.invoke(cli, [
            "store", "mykey", "myvalue",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "Stored credential" in result.output

        # Get credential
        result = runner.invoke(cli, [
            "get", "mykey",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "myvalue" in result.output

    def test_list_credentials(self, runner, temp_vault):
        """Test listing credentials."""
        # Initialize vault
        runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # Store some credentials
        runner.invoke(cli, [
            "store", "key1", "value1",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        runner.invoke(cli, [
            "store", "key2", "value2",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # List
        result = runner.invoke(cli, [
            "list",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "key1" in result.output
        assert "key2" in result.output

    def test_delete_credential(self, runner, temp_vault):
        """Test deleting a credential."""
        # Initialize and store
        runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        runner.invoke(cli, [
            "store", "delete_me", "temp_value",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # Delete with force flag
        result = runner.invoke(cli, [
            "delete", "delete_me",
            "--vault", temp_vault,
            "--password", "testpass123",
            "--force"
        ])
        assert result.exit_code == 0
        assert "Deleted credential" in result.output

    def test_rotate_credential(self, runner, temp_vault):
        """Test rotating a credential."""
        # Initialize and store
        runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        runner.invoke(cli, [
            "store", "rotate_key", "v1",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # Rotate
        result = runner.invoke(cli, [
            "rotate", "rotate_key", "v2",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "Rotated credential" in result.output

        # Verify new value
        result = runner.invoke(cli, [
            "get", "rotate_key", "--quiet",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert "v2" in result.output

    def test_quiet_mode(self, runner, temp_vault):
        """Test quiet output mode."""
        # Initialize and store
        runner.invoke(cli, [
            "init",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        runner.invoke(cli, [
            "store", "quiet_key", "quiet_value",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])

        # Get with quiet mode
        result = runner.invoke(cli, [
            "get", "quiet_key", "--quiet",
            "--vault", temp_vault,
            "--password", "testpass123"
        ])
        assert result.output.strip() == "quiet_value"
