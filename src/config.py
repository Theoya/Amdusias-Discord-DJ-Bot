"""Configuration management for the Discord DJ Bot."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class DiscordConfig:
    """Discord bot configuration."""

    token: str
    guild_id: Optional[str]
    command_prefix: str


@dataclass
class IcecastConfig:
    """Icecast server configuration (optional)."""

    host: str
    port: int
    mount: str
    url: str


@dataclass
class AudioConfig:
    """Audio streaming configuration."""

    bitrate: int
    sample_rate: int


@dataclass
class AudioSourceConfig:
    """Configuration for the selected audio source."""

    source_type: str  # 'local', 'icecast', 'url'
    device_index: Optional[int] = None  # For local audio devices
    url: Optional[str] = None  # For icecast/url sources
    bitrate: int = 128
    sample_rate: int = 48000


@dataclass
class BotConfig:
    """Complete bot configuration."""

    discord: DiscordConfig
    icecast: Optional[IcecastConfig]
    audio: AudioConfig
    audio_source: Optional[AudioSourceConfig] = None


class ConfigLoader:
    """Loads and validates configuration from environment variables."""

    @staticmethod
    def load_env(env_path: Optional[str] = None) -> None:
        """Load environment variables from .env file.

        Args:
            env_path: Optional path to .env file. If None, searches for .env in current directory.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

    @staticmethod
    def get_env_var(
        key: str, default: Optional[str] = None, required: bool = True
    ) -> str:
        """Get environment variable with optional default.

        Args:
            key: Environment variable name.
            default: Default value if variable is not set.
            required: Whether the variable is required.

        Returns:
            Environment variable value.

        Raises:
            ValueError: If required variable is not set.
        """
        value = os.getenv(key, default)
        if required and not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value or ""

    @classmethod
    def load_config(cls, env_path: Optional[str] = None) -> BotConfig:
        """Load complete bot configuration.

        Args:
            env_path: Optional path to .env file.

        Returns:
            Complete bot configuration.

        Raises:
            ValueError: If required configuration is missing.
        """
        cls.load_env(env_path)

        discord_config = DiscordConfig(
            token=cls.get_env_var("DISCORD_BOT_TOKEN"),
            guild_id=cls.get_env_var("DISCORD_GUILD_ID", required=False),
            command_prefix=cls.get_env_var("COMMAND_PREFIX", default="!"),
        )

        # Icecast is now optional
        icecast_url = cls.get_env_var("ICECAST_URL", required=False)
        icecast_config = None
        if icecast_url:
            icecast_config = IcecastConfig(
                host=cls.get_env_var("ICECAST_HOST", default="127.0.0.1"),
                port=int(cls.get_env_var("ICECAST_PORT", default="8000")),
                mount=cls.get_env_var("ICECAST_MOUNT", default="/live"),
                url=icecast_url,
            )

        audio_config = AudioConfig(
            bitrate=int(cls.get_env_var("AUDIO_BITRATE", default="128")),
            sample_rate=int(cls.get_env_var("AUDIO_SAMPLE_RATE", default="48000")),
        )

        return BotConfig(
            discord=discord_config,
            icecast=icecast_config,
            audio=audio_config,
            audio_source=None  # Will be set by CLI selection
        )
