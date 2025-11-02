"""Tests for Icecast stream reader."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiohttp import ClientError, ClientResponse, ClientSession
from src.stream_reader import IcecastStreamReader


class TestIcecastStreamReader:
    """Tests for IcecastStreamReader class."""

    def test_init(self) -> None:
        """Test stream reader initialization."""
        reader = IcecastStreamReader("http://localhost:8000/live", timeout=15)
        assert reader.get_stream_url() == "http://localhost:8000/live"
        assert not reader.is_connected()

    def test_get_stream_url(self) -> None:
        """Test getting stream URL."""
        url = "http://example.com:8000/stream"
        reader = IcecastStreamReader(url)
        assert reader.get_stream_url() == url

    def test_is_connected_initial(self) -> None:
        """Test is_connected returns False initially."""
        reader = IcecastStreamReader("http://localhost:8000/live")
        assert not reader.is_connected()

    @pytest.mark.asyncio
    async def test_connect_success(self) -> None:
        """Test successful connection to stream."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.raise_for_status = Mock()

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session

            await reader.connect()

            assert reader.is_connected()
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self) -> None:
        """Test connecting when already connected."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.raise_for_status = Mock()

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session

            await reader.connect()
            await reader.connect()  # Second call should log warning

            # Should only call get once (not twice)
            assert mock_session.get.call_count == 1

    @pytest.mark.asyncio
    async def test_connect_failure(self) -> None:
        """Test failed connection to stream."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(side_effect=ClientError("Connection failed"))
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session

            with pytest.raises(ClientError):
                await reader.connect()

            assert not reader.is_connected()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_stream_not_connected(self) -> None:
        """Test reading stream when not connected."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        with pytest.raises(RuntimeError, match="Not connected to stream"):
            async for _ in reader.read_stream():
                pass

    @pytest.mark.asyncio
    async def test_read_stream_success(self) -> None:
        """Test successfully reading stream data."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        # Mock response content
        mock_content = AsyncMock()
        test_chunks = [b"chunk1", b"chunk2", b"chunk3"]

        async def mock_iter_chunked(chunk_size: int):
            for chunk in test_chunks:
                yield chunk

        mock_content.iter_chunked = mock_iter_chunked

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.raise_for_status = Mock()
        mock_response.content = mock_content

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session

            await reader.connect()

            chunks = []
            async for chunk in reader.read_stream(chunk_size=1024):
                chunks.append(chunk)

            assert chunks == test_chunks

    @pytest.mark.asyncio
    async def test_read_stream_with_custom_chunk_size(self) -> None:
        """Test reading stream with custom chunk size."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        mock_content = AsyncMock()
        custom_chunk_size = 8192

        async def mock_iter_chunked(chunk_size: int):
            assert chunk_size == custom_chunk_size
            yield b"test_chunk"

        mock_content.iter_chunked = mock_iter_chunked

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.raise_for_status = Mock()
        mock_response.content = mock_content

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session

            await reader.connect()

            async for _ in reader.read_stream(chunk_size=custom_chunk_size):
                break

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        """Test closing stream connection."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.raise_for_status = Mock()
        mock_response.close = Mock()

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock(spec=ClientSession)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session

            await reader.connect()
            assert reader.is_connected()

            await reader.close()

            assert not reader.is_connected()
            mock_response.close.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self) -> None:
        """Test closing when not connected."""
        reader = IcecastStreamReader("http://localhost:8000/live")

        # Should not raise error
        await reader.close()
        assert not reader.is_connected()
