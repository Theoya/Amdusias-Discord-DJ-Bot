"""Icecast stream reader for fetching audio data."""

import asyncio
import logging
from typing import AsyncGenerator, Optional, Protocol
import aiohttp


logger = logging.getLogger(__name__)


class StreamReaderProtocol(Protocol):
    """Protocol for stream readers (for testing/mocking)."""

    async def read_stream(self, chunk_size: int) -> AsyncGenerator[bytes, None]:
        """Read stream in chunks.

        Args:
            chunk_size: Size of each chunk to read.

        Yields:
            Audio data chunks.
        """
        ...

    async def close(self) -> None:
        """Close the stream connection."""
        ...


class IcecastStreamReader:
    """Reads audio stream from Icecast server."""

    def __init__(self, stream_url: str, timeout: int = 10) -> None:
        """Initialize stream reader.

        Args:
            stream_url: URL of the Icecast stream.
            timeout: Connection timeout in seconds.
        """
        self._stream_url = stream_url
        self._timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._response: Optional[aiohttp.ClientResponse] = None
        self._is_connected = False

    def get_stream_url(self) -> str:
        """Get the configured stream URL.

        Returns:
            Stream URL.
        """
        return self._stream_url

    def is_connected(self) -> bool:
        """Check if currently connected to stream.

        Returns:
            True if connected, False otherwise.
        """
        return self._is_connected

    async def connect(self) -> None:
        """Establish connection to the Icecast stream.

        Raises:
            aiohttp.ClientError: If connection fails.
        """
        if self._is_connected:
            logger.warning("Already connected to stream")
            return

        logger.info(f"Connecting to Icecast stream: {self._stream_url}")

        self._session = aiohttp.ClientSession()
        timeout = aiohttp.ClientTimeout(total=self._timeout)

        try:
            self._response = await self._session.get(
                self._stream_url,
                timeout=timeout,
                headers={'Icy-MetaData': '0'}  # Disable metadata for simpler parsing
            )
            self._response.raise_for_status()
            self._is_connected = True
            logger.info("Successfully connected to stream")
        except Exception as e:
            await self.close()
            logger.error(f"Failed to connect to stream: {e}")
            raise

    async def read_stream(self, chunk_size: int = 4096) -> AsyncGenerator[bytes, None]:
        """Read stream in chunks.

        Args:
            chunk_size: Size of each chunk to read in bytes.

        Yields:
            Audio data chunks.

        Raises:
            RuntimeError: If not connected to stream.
        """
        if not self._is_connected or not self._response:
            raise RuntimeError("Not connected to stream. Call connect() first.")

        logger.info("Starting stream read")

        try:
            async for chunk in self._response.content.iter_chunked(chunk_size):
                if chunk:
                    yield chunk
        except asyncio.CancelledError:
            logger.info("Stream read cancelled")
            raise
        except Exception as e:
            logger.error(f"Error reading stream: {e}")
            raise

    async def close(self) -> None:
        """Close the stream connection and cleanup resources."""
        logger.info("Closing stream connection")

        self._is_connected = False

        if self._response:
            self._response.close()
            self._response = None

        if self._session:
            await self._session.close()
            self._session = None

        logger.info("Stream connection closed")
