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
    def test_enumerate_devices_windows(self, mock_system: Mock) -> None:
        """Test enumerating devices on Windows."""
        mock_system.return_value = "Windows"

        # Mock FFmpeg output
        mock_output = '''
[dshow @ 000001] DirectShow video devices
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Microphone (Realtek Audio)"
[dshow @ 000001]     Alternative name "@device_cm_{GUID}\\wave_{GUID}"
[dshow @ 000001]  "Stereo Mix (Realtek Audio)"
[dshow @ 000001]     Alternative name "@device_cm_{GUID}\\wave_{GUID}"
        '''

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            devices = AudioDeviceEnumerator.enumerate_devices()

            assert len(devices) == 2
            assert devices[0].name == "Microphone (Realtek Audio)"
            assert devices[0].device_id == "audio=Microphone (Realtek Audio)"
            assert devices[1].name == "Stereo Mix (Realtek Audio)"

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

    @patch("subprocess.run")
    @patch("platform.system")
    def test_enumerate_devices_timeout(
        self, mock_system: Mock, mock_run: Mock
    ) -> None:
        """Test error when FFmpeg times out."""
        mock_system.return_value = "Windows"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ffmpeg", timeout=10)

        with pytest.raises(RuntimeError, match="timed out"):
            AudioDeviceEnumerator.enumerate_devices()

    @patch("platform.system")
    def test_get_device_by_index(self, mock_system: Mock) -> None:
        """Test getting device by index."""
        mock_system.return_value = "Windows"

        mock_output = '''
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Test Device 1"
[dshow @ 000001]  "Test Device 2"
        '''

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            device = AudioDeviceEnumerator.get_device_by_index(2)

            assert device is not None
            assert device.index == 2
            assert device.name == "Test Device 2"

    @patch("platform.system")
    def test_get_device_by_index_invalid(self, mock_system: Mock) -> None:
        """Test getting device by invalid index."""
        mock_system.return_value = "Windows"

        mock_output = '''
[dshow @ 000001] DirectShow audio devices
[dshow @ 000001]  "Test Device 1"
        '''

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = mock_output
            mock_run.return_value = mock_result

            device = AudioDeviceEnumerator.get_device_by_index(99)

            assert device is None
