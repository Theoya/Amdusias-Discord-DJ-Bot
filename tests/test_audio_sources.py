"""Tests for audio source implementations."""

import pytest
from unittest.mock import Mock, patch
import discord
from src.audio_sources import (
    AudioSourceType,
    LocalAudioSource,
    IcecastAudioSource,
    URLAudioSource,
)
from src.audio_device import AudioDevice


class TestLocalAudioSource:
    """Tests for LocalAudioSource class."""

    def test_initialization(self) -> None:
        """Test LocalAudioSource initialization."""
        device = AudioDevice(
            index=1,
            name="Test Microphone",
            device_id="audio=Test Microphone",
            device_type="input",
        )

        source = LocalAudioSource(device=device, sample_rate=48000, bitrate=128)

        assert source.get_type() == AudioSourceType.LOCAL_DEVICE
        assert "Test Microphone" in source.get_description()

    @patch("platform.system")
    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_windows(
        self, mock_ffmpeg: Mock, mock_system: Mock
    ) -> None:
        """Test creating Discord source on Windows."""
        mock_system.return_value = "Windows"

        device = AudioDevice(
            index=1,
            name="Microphone",
            device_id="audio=Microphone",
            device_type="input",
        )

        source = LocalAudioSource(device=device)
        discord_source = source.create_discord_source()

        # Verify FFmpegPCMAudio was called with correct parameters
        mock_ffmpeg.assert_called_once()
        call_args = mock_ffmpeg.call_args

        assert "audio=Microphone" in str(call_args)
        assert "dshow" in str(call_args)

    @patch("platform.system")
    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_linux(
        self, mock_ffmpeg: Mock, mock_system: Mock
    ) -> None:
        """Test creating Discord source on Linux."""
        mock_system.return_value = "Linux"

        device = AudioDevice(
            index=1,
            name="pulse_device",
            device_id="pulse_device",
            device_type="input",
        )

        source = LocalAudioSource(device=device)
        discord_source = source.create_discord_source()

        mock_ffmpeg.assert_called_once()
        call_args = mock_ffmpeg.call_args

        assert "pulse" in str(call_args)

    @patch("platform.system")
    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_macos(
        self, mock_ffmpeg: Mock, mock_system: Mock
    ) -> None:
        """Test creating Discord source on macOS."""
        mock_system.return_value = "Darwin"

        device = AudioDevice(
            index=1,
            name="Built-in Microphone",
            device_id=":0",
            device_type="input",
        )

        source = LocalAudioSource(device=device)
        discord_source = source.create_discord_source()

        mock_ffmpeg.assert_called_once()
        call_args = mock_ffmpeg.call_args

        assert "avfoundation" in str(call_args)

    @patch("platform.system")
    def test_create_discord_source_unsupported_platform(
        self, mock_system: Mock
    ) -> None:
        """Test error on unsupported platform."""
        mock_system.return_value = "FreeBSD"

        device = AudioDevice(
            index=1,
            name="Test",
            device_id="test",
            device_type="input",
        )

        source = LocalAudioSource(device=device)

        with pytest.raises(RuntimeError, match="Unsupported platform"):
            source.create_discord_source()

    @patch("platform.system")
    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_ffmpeg_error(
        self, mock_ffmpeg: Mock, mock_system: Mock
    ) -> None:
        """Test error when FFmpeg fails."""
        mock_system.return_value = "Windows"
        mock_ffmpeg.side_effect = Exception("FFmpeg error")

        device = AudioDevice(
            index=1,
            name="Test",
            device_id="audio=Test",
            device_type="input",
        )

        source = LocalAudioSource(device=device)

        with pytest.raises(RuntimeError, match="Failed to connect to audio device"):
            source.create_discord_source()

    def test_cleanup(self) -> None:
        """Test cleanup method."""
        device = AudioDevice(
            index=1,
            name="Test",
            device_id="audio=Test",
            device_type="input",
        )

        source = LocalAudioSource(device=device)
        source.cleanup()  # Should not raise


class TestIcecastAudioSource:
    """Tests for IcecastAudioSource class."""

    def test_initialization(self) -> None:
        """Test IcecastAudioSource initialization."""
        source = IcecastAudioSource(url="http://example.com:8000/stream", bitrate=128)

        assert source.get_type() == AudioSourceType.ICECAST_STREAM
        assert "http://example.com:8000/stream" in source.get_description()

    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source(self, mock_ffmpeg: Mock) -> None:
        """Test creating Discord source from Icecast."""
        source = IcecastAudioSource(url="http://example.com:8000/stream")
        discord_source = source.create_discord_source()

        mock_ffmpeg.assert_called_once()
        call_args = mock_ffmpeg.call_args

        assert "http://example.com:8000/stream" in str(call_args)
        assert "reconnect" in str(call_args)

    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_error(self, mock_ffmpeg: Mock) -> None:
        """Test error when creating Discord source fails."""
        mock_ffmpeg.side_effect = Exception("Connection error")

        source = IcecastAudioSource(url="http://example.com:8000/stream")

        with pytest.raises(RuntimeError, match="Failed to connect to Icecast stream"):
            source.create_discord_source()

    def test_cleanup(self) -> None:
        """Test cleanup method."""
        source = IcecastAudioSource(url="http://example.com:8000/stream")
        source.cleanup()  # Should not raise


class TestURLAudioSource:
    """Tests for URLAudioSource class."""

    def test_initialization(self) -> None:
        """Test URLAudioSource initialization."""
        source = URLAudioSource(url="http://example.com/audio.mp3", bitrate=192)

        assert source.get_type() == AudioSourceType.URL_STREAM
        assert "http://example.com/audio.mp3" in source.get_description()

    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source(self, mock_ffmpeg: Mock) -> None:
        """Test creating Discord source from URL."""
        source = URLAudioSource(url="http://example.com/audio.mp3")
        discord_source = source.create_discord_source()

        mock_ffmpeg.assert_called_once()
        call_args = mock_ffmpeg.call_args

        assert "http://example.com/audio.mp3" in str(call_args)

    @patch("discord.FFmpegPCMAudio")
    def test_create_discord_source_error(self, mock_ffmpeg: Mock) -> None:
        """Test error when creating Discord source fails."""
        mock_ffmpeg.side_effect = Exception("Network error")

        source = URLAudioSource(url="http://example.com/audio.mp3")

        with pytest.raises(RuntimeError, match="Failed to connect to URL"):
            source.create_discord_source()

    def test_cleanup(self) -> None:
        """Test cleanup method."""
        source = URLAudioSource(url="http://example.com/audio.mp3")
        source.cleanup()  # Should not raise
