"""Tests for audio source."""

import pytest
from unittest.mock import AsyncMock, Mock
from src.audio_source import IcecastAudioSource
from src.stream_reader import StreamReaderProtocol


class MockStreamReader:
    """Mock stream reader for testing."""

    def __init__(self) -> None:
        self.read_stream = AsyncMock()
        self.close = AsyncMock()


class TestIcecastAudioSource:
    """Tests for IcecastAudioSource class."""

    def test_init(self) -> None:
        """Test audio source initialization."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader, chunk_size=4096)

        assert not source.is_active()

    def test_init_with_custom_chunk_size(self) -> None:
        """Test initialization with custom chunk size."""
        mock_reader = MockStreamReader()
        custom_chunk_size = 8192
        source = IcecastAudioSource(mock_reader, chunk_size=custom_chunk_size)

        assert not source.is_active()

    def test_is_active_initial(self) -> None:
        """Test is_active returns False initially."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        assert not source.is_active()

    @pytest.mark.asyncio
    async def test_start(self) -> None:
        """Test starting audio source."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        await source.start()
        assert source.is_active()

    @pytest.mark.asyncio
    async def test_start_already_started(self) -> None:
        """Test starting when already started."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        await source.start()

        with pytest.raises(RuntimeError, match="Audio source already started"):
            await source.start()

    def test_read_when_not_active(self) -> None:
        """Test reading when audio source is not active."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        result = source.read()
        assert result == b""

    def test_read_when_active(self) -> None:
        """Test reading when audio source is active."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        # Start the source (this is async but we're testing sync read method)
        # In actual implementation, read() would return data
        # For now it returns empty as documented in the code
        result = source.read()
        assert isinstance(result, bytes)

    def test_cleanup(self) -> None:
        """Test cleanup of audio source."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        source.cleanup()
        assert not source.is_active()

    @pytest.mark.asyncio
    async def test_stop(self) -> None:
        """Test stopping audio source."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        await source.start()
        assert source.is_active()

        await source.stop()
        assert not source.is_active()

    @pytest.mark.asyncio
    async def test_stop_when_not_started(self) -> None:
        """Test stopping when not started."""
        mock_reader = MockStreamReader()
        source = IcecastAudioSource(mock_reader)

        # Should not raise error
        await source.stop()
        assert not source.is_active()
