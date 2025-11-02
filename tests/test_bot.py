"""Tests for Discord bot."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import discord
from discord.ext import commands
from src.bot import DJBot
from src.config import BotConfig, DiscordConfig, IcecastConfig, AudioConfig
from src.audio_sources import IcecastAudioSource, AudioSourceType


class TestDJBot:
    """Tests for DJBot class."""

    @pytest.fixture
    def mock_config(self) -> BotConfig:
        """Create mock configuration for testing."""
        return BotConfig(
            discord=DiscordConfig(
                token="test_token", guild_id="123456", command_prefix="!"
            ),
            icecast=IcecastConfig(
                host="localhost",
                port=8000,
                mount="/live",
                url="http://localhost:8000/live",
            ),
            audio=AudioConfig(bitrate=128, sample_rate=48000),
        )

    @pytest.fixture
    def mock_audio_source(self) -> Mock:
        """Create mock audio source for testing."""
        mock_source = Mock()
        mock_source.get_type.return_value = AudioSourceType.ICECAST_STREAM
        mock_source.get_description.return_value = "Test Audio Source"
        mock_source.create_discord_source.return_value = Mock(spec=discord.AudioSource)
        mock_source.cleanup = Mock()
        return mock_source

    def test_init(self, mock_config: BotConfig, mock_audio_source: Mock) -> None:
        """Test bot initialization."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        assert bot.get_config() == mock_config
        assert bot.get_voice_client() is None
        assert not bot.is_streaming()
        assert bot.command_prefix == "!"

    def test_get_config(self, mock_config: BotConfig, mock_audio_source: Mock) -> None:
        """Test getting bot configuration."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)
        assert bot.get_config() == mock_config

    def test_get_voice_client_none(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test getting voice client when not connected."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)
        assert bot.get_voice_client() is None

    def test_is_streaming_false(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test is_streaming returns False when not streaming."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)
        assert not bot.is_streaming()

    def test_is_streaming_with_voice_client_not_playing(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test is_streaming when connected but not playing."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_voice_client = Mock(spec=discord.VoiceClient)
        mock_voice_client.is_playing = Mock(return_value=False)
        bot._voice_client = mock_voice_client

        assert not bot.is_streaming()

    def test_is_streaming_true(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test is_streaming returns True when streaming."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_voice_client = Mock(spec=discord.VoiceClient)
        mock_voice_client.is_playing = Mock(return_value=True)
        bot._voice_client = mock_voice_client

        assert bot.is_streaming()

    @pytest.mark.asyncio
    async def test_on_ready(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test on_ready event handler."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)
        bot.user = Mock()
        bot.user.__str__ = Mock(return_value="TestBot")
        bot.guilds = [Mock(), Mock()]

        # Should not raise error
        await bot.on_ready()

    @pytest.mark.asyncio
    async def test_cleanup_with_voice_client(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test cleanup with active voice client."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_voice_client = AsyncMock(spec=discord.VoiceClient)
        mock_voice_client.is_connected = Mock(return_value=True)
        mock_voice_client.disconnect = AsyncMock()
        bot._voice_client = mock_voice_client

        with patch.object(bot, "close", new_callable=AsyncMock) as mock_close:
            await bot.cleanup()
            mock_voice_client.disconnect.assert_called_once()
            mock_audio_source.cleanup.assert_called_once()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_without_voice_client(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test cleanup without voice client."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        with patch.object(bot, "close", new_callable=AsyncMock) as mock_close:
            await bot.cleanup()
            mock_audio_source.cleanup.assert_called_once()
            mock_close.assert_called_once()

    def test_commands_registered(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test that all commands are registered."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        command_names = [cmd.name for cmd in bot.commands]

        assert "join" in command_names
        assert "leave" in command_names
        assert "play" in command_names
        assert "stop" in command_names

    @pytest.mark.asyncio
    async def test_join_command_not_in_voice(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test join command when user is not in voice channel."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        # Create mock context
        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.author.voice = None
        mock_ctx.send = AsyncMock()

        # Get the join command
        join_cmd = bot.get_command("join")
        await join_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "need to be in a voice channel" in mock_ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_join_command_already_connected(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test join command when already connected."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_voice_client = Mock(spec=discord.VoiceClient)
        mock_voice_client.is_connected = Mock(return_value=True)
        bot._voice_client = mock_voice_client

        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.author.voice = Mock()
        mock_ctx.author.voice.channel = Mock()
        mock_ctx.send = AsyncMock()

        join_cmd = bot.get_command("join")
        await join_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "Already connected" in mock_ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_leave_command_not_connected(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test leave command when not connected."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.send = AsyncMock()

        leave_cmd = bot.get_command("leave")
        await leave_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "Not connected" in mock_ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_play_command_not_connected(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test play command when not connected to voice."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.send = AsyncMock()

        play_cmd = bot.get_command("play")
        await play_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "Not connected to a voice channel" in mock_ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_stop_command_not_connected(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test stop command when not connected."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.send = AsyncMock()

        stop_cmd = bot.get_command("stop")
        await stop_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "Not connected" in mock_ctx.send.call_args[0][0]

    @pytest.mark.asyncio
    async def test_stop_command_not_playing(
        self, mock_config: BotConfig, mock_audio_source: Mock
    ) -> None:
        """Test stop command when not playing audio."""
        bot = DJBot(mock_config, audio_source=mock_audio_source)

        mock_voice_client = Mock(spec=discord.VoiceClient)
        mock_voice_client.is_playing = Mock(return_value=False)
        bot._voice_client = mock_voice_client

        mock_ctx = AsyncMock(spec=commands.Context)
        mock_ctx.send = AsyncMock()

        stop_cmd = bot.get_command("stop")
        await stop_cmd.callback(mock_ctx)

        mock_ctx.send.assert_called_once()
        assert "Not currently playing" in mock_ctx.send.call_args[0][0]
