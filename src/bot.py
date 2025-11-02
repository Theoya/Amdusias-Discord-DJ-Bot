"""Discord bot implementation for DJ streaming."""

import logging
from typing import Optional, Union, cast
import discord
from discord.ext import commands
from src.config import BotConfig
from src.audio_sources import AudioSourceProtocol


logger = logging.getLogger(__name__)


class DJBot(commands.Bot):
    """Discord DJ bot that streams audio from various sources."""

    def __init__(self, config: BotConfig, audio_source: AudioSourceProtocol) -> None:
        """Initialize the DJ bot.

        Args:
            config: Bot configuration.
            audio_source: Audio source to stream from.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(command_prefix=config.discord.command_prefix, intents=intents)

        self._config = config
        self._audio_source = audio_source
        self._voice_client: Optional[discord.VoiceClient] = None

        # Register commands
        self.add_command(self._create_join_command())
        self.add_command(self._create_leave_command())
        self.add_command(self._create_play_command())
        self.add_command(self._create_stop_command())

    def get_config(self) -> BotConfig:
        """Get bot configuration.

        Returns:
            Bot configuration.
        """
        return self._config

    def get_voice_client(self) -> Optional[discord.VoiceClient]:
        """Get current voice client.

        Returns:
            Voice client if connected, None otherwise.
        """
        return self._voice_client

    def is_streaming(self) -> bool:
        """Check if currently streaming audio.

        Returns:
            True if streaming, False otherwise.
        """
        return self._voice_client is not None and self._voice_client.is_playing()

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Bot logged in as {self.user}")
        logger.info(f"Connected to {len(self.guilds)} guilds")

    def _create_join_command(self) -> commands.Command:
        """Create the join voice channel command.

        Returns:
            Join command.
        """

        @commands.command(name="join")
        async def join(ctx: commands.Context) -> None:
            """Join the voice channel of the user who invoked the command."""
            # Type guard: ctx.author must be a Member to have voice attribute
            if not isinstance(ctx.author, discord.Member):
                await ctx.send("This command can only be used in a server.")
                return

            if not ctx.author.voice:
                await ctx.send("You need to be in a voice channel to use this command.")
                return

            channel = ctx.author.voice.channel
            if channel is None:
                await ctx.send("Could not determine your voice channel.")
                return

            if self._voice_client and self._voice_client.is_connected():
                await ctx.send("Already connected to a voice channel.")
                return

            try:
                # channel is VoiceChannel or StageChannel, both have connect()
                self._voice_client = await channel.connect()  # type: ignore[union-attr]
                await ctx.send(f"Joined {channel.name}")
                logger.info(f"Joined voice channel: {channel.name}")
            except Exception as e:
                logger.error(f"Failed to join voice channel: {e}")
                await ctx.send(f"Failed to join voice channel: {e}")

        return join

    def _create_leave_command(self) -> commands.Command:
        """Create the leave voice channel command.

        Returns:
            Leave command.
        """

        @commands.command(name="leave")
        async def leave(ctx: commands.Context) -> None:
            """Leave the current voice channel."""
            if not self._voice_client or not self._voice_client.is_connected():
                await ctx.send("Not connected to a voice channel.")
                return

            await self._voice_client.disconnect()
            self._voice_client = None
            await ctx.send("Disconnected from voice channel")
            logger.info("Left voice channel")

        return leave

    def _create_play_command(self) -> commands.Command:
        """Create the play stream command.

        Returns:
            Play command.
        """

        @commands.command(name="play")
        async def play(ctx: commands.Context) -> None:
            """Start streaming audio from the configured audio source."""
            # Auto-join if not connected
            if not self._voice_client or not self._voice_client.is_connected():
                # Type guard: ctx.author must be a Member to have voice attribute
                if not isinstance(ctx.author, discord.Member):
                    await ctx.send("This command can only be used in a server.")
                    return

                if not ctx.author.voice:
                    await ctx.send("You need to be in a voice channel to use this command.")
                    return

                channel = ctx.author.voice.channel
                if channel is None:
                    await ctx.send("Could not determine your voice channel.")
                    return

                try:
                    # Join the user's voice channel
                    self._voice_client = await channel.connect()  # type: ignore[union-attr]
                    await ctx.send(f"Joined {channel.name}")
                    logger.info(f"Auto-joined voice channel: {channel.name}")
                except Exception as e:
                    logger.error(f"Failed to join voice channel: {e}")
                    await ctx.send(f"Failed to join voice channel: {e}")
                    return

            if self._voice_client.is_playing():
                await ctx.send("Already playing audio.")
                return

            try:
                # Create Discord audio source from the configured source
                discord_audio = self._audio_source.create_discord_source()

                # Start playing
                self._voice_client.play(
                    discord_audio,
                    after=lambda e: logger.error(f"Player error: {e}") if e else None,
                )

                description = self._audio_source.get_description()
                await ctx.send(f"Now streaming: {description}")
                logger.info(f"Started streaming: {description}")

            except Exception as e:
                logger.error(f"Failed to start streaming: {e}")
                await ctx.send(f"Failed to start streaming: {e}")

        return play

    def _create_stop_command(self) -> commands.Command:
        """Create the stop streaming command.

        Returns:
            Stop command.
        """

        @commands.command(name="stop")
        async def stop(ctx: commands.Context) -> None:
            """Stop streaming audio."""
            if not self._voice_client:
                await ctx.send("Not connected to a voice channel.")
                return

            if not self._voice_client.is_playing():
                await ctx.send("Not currently playing audio.")
                return

            self._voice_client.stop()
            await ctx.send("Stopped streaming")
            logger.info("Stopped streaming")

        return stop

    async def cleanup(self) -> None:
        """Cleanup bot resources."""
        logger.info("Cleaning up bot resources")

        if self._voice_client and self._voice_client.is_connected():
            await self._voice_client.disconnect()

        # Cleanup audio source
        self._audio_source.cleanup()

        await self.close()
