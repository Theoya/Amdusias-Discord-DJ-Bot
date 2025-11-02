"""Tests for configuration management."""

import os
import pytest
from unittest.mock import patch, mock_open
from src.config import (
    ConfigLoader,
    BotConfig,
    DiscordConfig,
    AudioConfig,
)


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_env_with_path(self) -> None:
        """Test loading environment variables from specific path."""
        with patch("src.config.load_dotenv") as mock_load:
            ConfigLoader.load_env("/path/to/.env")
            mock_load.assert_called_once_with("/path/to/.env")

    def test_load_env_without_path(self) -> None:
        """Test loading environment variables from default path."""
        with patch("src.config.load_dotenv") as mock_load:
            ConfigLoader.load_env()
            mock_load.assert_called_once_with()

    def test_get_env_var_required_exists(self) -> None:
        """Test getting required environment variable that exists."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = ConfigLoader.get_env_var("TEST_VAR")
            assert result == "test_value"

    def test_get_env_var_required_missing(self) -> None:
        """Test getting required environment variable that is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Required environment variable 'TEST_VAR' is not set"
            ):
                ConfigLoader.get_env_var("TEST_VAR")

    def test_get_env_var_optional_exists(self) -> None:
        """Test getting optional environment variable that exists."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = ConfigLoader.get_env_var("TEST_VAR", required=False)
            assert result == "test_value"

    def test_get_env_var_optional_missing_with_default(self) -> None:
        """Test getting optional environment variable with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = ConfigLoader.get_env_var(
                "TEST_VAR", default="default_value", required=False
            )
            assert result == "default_value"

    def test_get_env_var_optional_missing_no_default(self) -> None:
        """Test getting optional environment variable without default."""
        with patch.dict(os.environ, {}, clear=True):
            result = ConfigLoader.get_env_var("TEST_VAR", required=False)
            assert result == ""

    def test_load_config_success(self) -> None:
        """Test loading complete configuration successfully."""
        env_vars = {
            "DISCORD_BOT_TOKEN": "test_token",
            "DISCORD_GUILD_ID": "123456789",
            "COMMAND_PREFIX": "!",
            "AUDIO_BITRATE": "128",
            "AUDIO_SAMPLE_RATE": "48000",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("src.config.load_dotenv"):
                config = ConfigLoader.load_config()

                assert isinstance(config, BotConfig)
                assert config.discord.token == "test_token"
                assert config.discord.guild_id == "123456789"
                assert config.discord.command_prefix == "!"
                assert config.audio.bitrate == 128
                assert config.audio.sample_rate == 48000

    def test_load_config_with_defaults(self) -> None:
        """Test loading configuration with default values."""
        env_vars = {
            "DISCORD_BOT_TOKEN": "test_token",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("src.config.load_dotenv"):
                config = ConfigLoader.load_config()

                assert config.discord.token == "test_token"
                assert config.discord.guild_id == ""
                assert config.discord.command_prefix == "!"
                assert config.audio.bitrate == 128
                assert config.audio.sample_rate == 48000

    def test_load_config_missing_required(self) -> None:
        """Test loading configuration with missing required variables."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.config.load_dotenv"):
                with pytest.raises(ValueError, match="DISCORD_BOT_TOKEN"):
                    ConfigLoader.load_config()


class TestDiscordConfig:
    """Tests for DiscordConfig dataclass."""

    def test_discord_config_creation(self) -> None:
        """Test creating Discord configuration."""
        config = DiscordConfig(
            token="test_token", guild_id="123456", command_prefix="!"
        )

        assert config.token == "test_token"
        assert config.guild_id == "123456"
        assert config.command_prefix == "!"


class TestAudioConfig:
    """Tests for AudioConfig dataclass."""

    def test_audio_config_creation(self) -> None:
        """Test creating Audio configuration."""
        config = AudioConfig(bitrate=128, sample_rate=48000)

        assert config.bitrate == 128
        assert config.sample_rate == 48000
