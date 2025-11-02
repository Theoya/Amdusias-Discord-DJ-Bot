"""Custom audio source for Discord voice streaming."""

import asyncio
import logging
from typing import Optional
import discord
from src.stream_reader import StreamReaderProtocol


logger = logging.getLogger(__name__)


class IcecastAudioSource(discord.AudioSource):
    """Audio source that reads from an Icecast stream."""

    def __init__(
        self, stream_reader: StreamReaderProtocol, chunk_size: int = 3840
    ) -> None:
        """Initialize audio source.

        Args:
            stream_reader: Stream reader instance.
            chunk_size: Size of audio chunks (default 3840 bytes = 20ms at 48kHz stereo).
        """
        self._stream_reader = stream_reader
        self._chunk_size = chunk_size
        self._stream_iterator: Optional[asyncio.Task] = None
        self._buffer = bytearray()
        self._is_active = False

    def is_active(self) -> bool:
        """Check if audio source is active.

        Returns:
            True if active, False otherwise.
        """
        return self._is_active

    async def start(self) -> None:
        """Start reading from the stream.

        Raises:
            RuntimeError: If already started.
        """
        if self._is_active:
            raise RuntimeError("Audio source already started")

        logger.info("Starting audio source")
        self._is_active = True

    def read(self) -> bytes:
        """Read audio data for Discord.

        This is called by Discord.py to get audio frames.
        Returns 20ms of audio at a time (3840 bytes for 48kHz stereo PCM).

        Returns:
            Audio data chunk, or empty bytes if no data available.
        """
        if not self._is_active:
            return b""

        # Note: This is a synchronous method required by discord.AudioSource
        # In a real implementation, you'd need to handle async/sync bridge
        # For now, this returns empty - actual implementation would require
        # running the async read in a separate thread or using discord.FFmpegPCMAudio
        return b""

    def cleanup(self) -> None:
        """Cleanup resources when audio source is destroyed."""
        logger.info("Cleaning up audio source")
        self._is_active = False
        self._buffer.clear()

    async def stop(self) -> None:
        """Stop reading from the stream."""
        logger.info("Stopping audio source")
        self._is_active = False
        self.cleanup()
