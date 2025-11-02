"""Tests for audio source factory."""

import pytest
from unittest.mock import Mock, patch
from src.audio_source_factory import AudioSourceFactory
from src.audio_sources import LocalAudioSource, IcecastAudioSource, URLAudioSource
from src.audio_device import AudioDevice


class TestAudioSourceFactory:
    """Tests for AudioSourceFactory class."""

    def test_create_local_source(self) -> None:
        """Test creating a local audio source."""
        device = AudioDevice(
            index=1,
            name="Test Device",
            device_id="audio=Test Device",
            device_type="input",
        )

        source = AudioSourceFactory.create_local_source(
            device=device, sample_rate=48000, bitrate=128
        )

        assert isinstance(source, LocalAudioSource)
        assert "Test Device" in source.get_description()

    @patch("src.audio_source_factory.AudioDeviceEnumerator.get_device_by_index")
    def test_create_local_source_by_index(self, mock_get_device: Mock) -> None:
        """Test creating a local audio source by index."""
        mock_device = AudioDevice(
            index=2,
            name="Device 2",
            device_id="audio=Device 2",
            device_type="input",
        )
        mock_get_device.return_value = mock_device

        source = AudioSourceFactory.create_local_source_by_index(device_index=2)

        assert isinstance(source, LocalAudioSource)
        mock_get_device.assert_called_once_with(2)

    @patch("src.audio_source_factory.AudioDeviceEnumerator.get_device_by_index")
    def test_create_local_source_by_index_invalid(
        self, mock_get_device: Mock
    ) -> None:
        """Test error when device index is invalid."""
        mock_get_device.return_value = None

        with pytest.raises(ValueError, match="No audio device found with index"):
            AudioSourceFactory.create_local_source_by_index(device_index=99)

    def test_create_icecast_source(self) -> None:
        """Test creating an Icecast audio source."""
        source = AudioSourceFactory.create_icecast_source(
            url="http://example.com:8000/stream", bitrate=128
        )

        assert isinstance(source, IcecastAudioSource)
        assert "http://example.com:8000/stream" in source.get_description()

    def test_create_url_source(self) -> None:
        """Test creating a URL audio source."""
        source = AudioSourceFactory.create_url_source(
            url="http://example.com/audio.mp3", bitrate=192
        )

        assert isinstance(source, URLAudioSource)
        assert "http://example.com/audio.mp3" in source.get_description()

    @patch("src.audio_source_factory.AudioDeviceEnumerator.get_device_by_index")
    def test_create_from_config_local(self, mock_get_device: Mock) -> None:
        """Test creating local source from config."""
        mock_device = AudioDevice(
            index=1,
            name="Test Device",
            device_id="audio=Test Device",
            device_type="input",
        )
        mock_get_device.return_value = mock_device

        config = {"device_index": 1, "sample_rate": 48000, "bitrate": 128}

        source = AudioSourceFactory.create_from_config(
            source_type="local", config=config
        )

        assert isinstance(source, LocalAudioSource)
        mock_get_device.assert_called_once_with(1)

    def test_create_from_config_local_missing_index(self) -> None:
        """Test error when creating local source without device_index."""
        config = {"sample_rate": 48000, "bitrate": 128}

        with pytest.raises(ValueError, match="requires 'device_index'"):
            AudioSourceFactory.create_from_config(source_type="local", config=config)

    def test_create_from_config_icecast(self) -> None:
        """Test creating Icecast source from config."""
        config = {"url": "http://example.com:8000/stream", "bitrate": 128}

        source = AudioSourceFactory.create_from_config(
            source_type="icecast", config=config
        )

        assert isinstance(source, IcecastAudioSource)

    def test_create_from_config_icecast_missing_url(self) -> None:
        """Test error when creating Icecast source without URL."""
        config = {"bitrate": 128}

        with pytest.raises(ValueError, match="requires 'url'"):
            AudioSourceFactory.create_from_config(source_type="icecast", config=config)

    def test_create_from_config_url(self) -> None:
        """Test creating URL source from config."""
        config = {"url": "http://example.com/audio.mp3", "bitrate": 192}

        source = AudioSourceFactory.create_from_config(source_type="url", config=config)

        assert isinstance(source, URLAudioSource)

    def test_create_from_config_url_missing_url(self) -> None:
        """Test error when creating URL source without URL."""
        config = {"bitrate": 192}

        with pytest.raises(ValueError, match="requires 'url'"):
            AudioSourceFactory.create_from_config(source_type="url", config=config)

    def test_create_from_config_invalid_type(self) -> None:
        """Test error when creating source with invalid type."""
        config = {"url": "http://example.com/audio.mp3"}

        with pytest.raises(ValueError, match="Unknown audio source type"):
            AudioSourceFactory.create_from_config(
                source_type="invalid", config=config
            )

    def test_create_from_config_case_insensitive(self) -> None:
        """Test that source type is case insensitive."""
        config = {"url": "http://example.com:8000/stream", "bitrate": 128}

        source = AudioSourceFactory.create_from_config(
            source_type="ICECAST", config=config
        )

        assert isinstance(source, IcecastAudioSource)
