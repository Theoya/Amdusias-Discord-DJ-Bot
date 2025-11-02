"""Tests for audio device enumeration."""

import pytest
import subprocess
from unittest.mock import Mock, patch
from src.audio_device import AudioDevice, AudioDeviceEnumerator


class TestAudioDevice:
    """Tests for AudioDevice dataclass."""

    def test_audio_device_creation(self) -> None:
        """Test creating an AudioDevice instance."""
        device = AudioDevice(
            index=1,
            name="Test Device",
            device_id="audio=Test Device",
            device_type="input",
        )

        assert device.index == 1
        assert device.name == "Test Device"
        assert device.device_id == "audio=Test Device"
        assert device.device_type == "input"


class TestAudioDeviceEnumerator:
    """Tests for AudioDeviceEnumerator class."""

    def test_get_system_type(self) -> None:
        """Test getting system type."""
        system_type = AudioDeviceEnumerator.get_system_type()
        assert system_type in ["windows", "linux", "darwin"]

    @patch("platform.system")
    @patch("pyaudiowpatch.PyAudio", create=True)
    def test_enumerate_devices_windows(
        self, mock_pyaudio_class: Mock, mock_system: Mock
    ) -> None:
        """Test enumerating devices on Windows."""
        mock_system.return_value = "Windows"

        # Mock pyaudiowpatch module to prevent real WASAPI enumeration
        mock_pyaudio_instance = Mock()
        mock_pyaudio_instance.get_device_count.return_value = 0
        mock_pyaudio_instance.terminate.return_value = None
        mock_pyaudio_class.return_value = mock_pyaudio_instance

        # Mock FFmpeg output
        mock_output = """
[dshow @ 000001] DirectShow video devices
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Microphone (Realtek Audio)" (audio)
[dshow @ 000001]     Alternative name "@device_cm_{GUID}\\wave_{GUID}"
[dshow @ 000001]  "Stereo Mix (Realtek Audio)" (audio)
[dshow @ 000001]     Alternative name "@device_cm_{GUID}\\wave_{GUID}"
        """

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            devices = AudioDeviceEnumerator.enumerate_devices()

            assert len(devices) == 2
            assert devices[0].name == "Microphone (Realtek Audio) [Microphone]"
            assert devices[0].device_id == "dshow:audio=Microphone (Realtek Audio)"
            assert devices[1].name == "Stereo Mix (Realtek Audio) [System Audio]"

    @patch("platform.system")
    def test_enumerate_devices_unsupported_os(self, mock_system: Mock) -> None:
        """Test enumerating devices on unsupported OS."""
        mock_system.return_value = "FreeBSD"

        with pytest.raises(RuntimeError, match="Unsupported operating system"):
            AudioDeviceEnumerator.enumerate_devices()

    @patch("subprocess.run")
    @patch("platform.system")
    def test_enumerate_devices_ffmpeg_not_found(
        self, mock_system: Mock, mock_run: Mock
    ) -> None:
        """Test error when FFmpeg is not found."""
        mock_system.return_value = "Windows"
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError, match="FFmpeg not found"):
            AudioDeviceEnumerator.enumerate_devices()

    @patch("pyaudiowpatch.PyAudio", create=True)
    @patch("subprocess.run")
    @patch("platform.system")
    def test_enumerate_devices_timeout(
        self, mock_system: Mock, mock_run: Mock, mock_pyaudio_class: Mock
    ) -> None:
        """Test that FFmpeg timeout is handled gracefully (logs warning, doesn't raise)."""
        mock_system.return_value = "Windows"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ffmpeg", timeout=10)

        # Mock pyaudiowpatch to return no devices
        mock_pyaudio_instance = Mock()
        mock_pyaudio_instance.get_device_count.return_value = 0
        mock_pyaudio_instance.terminate.return_value = None
        mock_pyaudio_class.return_value = mock_pyaudio_instance

        # Should return empty list but not raise (just logs warning)
        devices = AudioDeviceEnumerator.enumerate_devices()
        assert devices == []

    @patch("platform.system")
    @patch("pyaudiowpatch.PyAudio", create=True)
    def test_get_device_by_index(
        self, mock_pyaudio_class: Mock, mock_system: Mock
    ) -> None:
        """Test getting device by index."""
        mock_system.return_value = "Windows"

        # Mock pyaudiowpatch to return no devices
        mock_pyaudio_instance = Mock()
        mock_pyaudio_instance.get_device_count.return_value = 0
        mock_pyaudio_instance.terminate.return_value = None
        mock_pyaudio_class.return_value = mock_pyaudio_instance

        mock_output = """
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Test Device 1" (audio)
[dshow @ 000001]  "Test Device 2" (audio)
        """

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            device = AudioDeviceEnumerator.get_device_by_index(2)

            assert device is not None
            assert device.index == 2
            assert device.name == "Test Device 2 [Microphone]"

    @patch("platform.system")
    @patch("pyaudiowpatch.PyAudio", create=True)
    def test_get_device_by_index_invalid(
        self, mock_pyaudio_class: Mock, mock_system: Mock
    ) -> None:
        """Test getting device by invalid index."""
        mock_system.return_value = "Windows"

        # Mock pyaudiowpatch to return no devices
        mock_pyaudio_instance = Mock()
        mock_pyaudio_instance.get_device_count.return_value = 0
        mock_pyaudio_instance.terminate.return_value = None
        mock_pyaudio_class.return_value = mock_pyaudio_instance

        mock_output = """
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Test Device 1" (audio)
        """

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            device = AudioDeviceEnumerator.get_device_by_index(99)

            assert device is None
