"""Discord bot implementation for DJ streaming."""

import logging
from typing import Optional
import discord
from discord.ext import commands
from src.config import BotConfig
from src.stream_reader import IcecastStreamReader


logger = logging.getLogger(__name__)


class DJBot(commands.Bot):
    """Discord DJ bot that streams audio from Icecast server."""

    def __init__(self, config: BotConfig) -> None:
        """Initialize the DJ bot.

        Args:
            config: Bot configuration.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix=config.discord.command_prefix,
            intents=intents
        )

        self._config = config
        self._stream_reader: Optional[IcecastStreamReader] = None
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
            if not ctx.author.voice:
                await ctx.send("You need to be in a voice channel to use this command.")
                return

            channel = ctx.author.voice.channel

            if self._voice_client and self._voice_client.is_connected():
                await ctx.send("Already connected to a voice channel.")
                return

            try:
                self._voice_client = await channel.connect()
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
            """Start streaming audio from the Icecast server."""
            if not self._voice_client or not self._voice_client.is_connected():
                await ctx.send("Not connected to a voice channel. Use !join first.")
                return

            if self._voice_client.is_playing():
                await ctx.send("Already playing audio.")
                return

            try:
                # Use FFmpeg to read from Icecast stream and convert to Discord format
                stream_url = self._config.icecast.url

                # FFmpeg options for better streaming
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn -b:a 128k'
                }

                audio_source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
                self._voice_client.play(
                    audio_source,
                    after=lambda e: logger.error(f"Player error: {e}") if e else None
                )

                await ctx.send(f"Now streaming from {stream_url}")
                logger.info(f"Started streaming from {stream_url}")

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

        if self._stream_reader:
            await self._stream_reader.close()

        await self.close()
