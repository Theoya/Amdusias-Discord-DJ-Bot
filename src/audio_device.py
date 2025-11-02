"""Audio device enumeration and management."""

import logging
import platform
import subprocess
import re
from typing import List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Represents an audio device."""

    index: int
    name: str
    device_id: str
    device_type: str  # 'input' or 'output'


class AudioDeviceEnumerator:
    """Enumerates available audio devices on the system."""

    @staticmethod
    def get_system_type() -> str:
        """Get the operating system type.

        Returns:
            'windows', 'linux', or 'darwin' (macOS).
        """
        return platform.system().lower()

    @staticmethod
    def enumerate_devices() -> List[AudioDevice]:
        """Enumerate all available audio input devices.

        Returns:
            List of available audio devices.

        Raises:
            RuntimeError: If FFmpeg is not available or device enumeration fails.
        """
        system = AudioDeviceEnumerator.get_system_type()

        if system == "windows":
            return AudioDeviceEnumerator._enumerate_windows_devices()
        elif system == "linux":
            return AudioDeviceEnumerator._enumerate_linux_devices()
        elif system == "darwin":
            return AudioDeviceEnumerator._enumerate_macos_devices()
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

    @staticmethod
    def _enumerate_windows_devices() -> List[AudioDevice]:
        """Enumerate audio devices on Windows using DirectShow and WASAPI loopback.

        Returns:
            List of available audio devices.

        Raises:
            RuntimeError: If FFmpeg is not available.
        """
        devices = []
        device_index = 1

        # First, enumerate WASAPI loopback devices (system audio capture)
        try:
            import pyaudiowpatch as pyaudio

            p = pyaudio.PyAudio()

            # Get all loopback devices
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)

                # Only include loopback devices (system audio output capture)
                if info.get("isLoopbackDevice", False):
                    device_name = info["name"]
                    # Clean up the name - remove " [Loopback]" suffix if present
                    display_name = device_name.replace(" [Loopback]", "")

                    devices.append(
                        AudioDevice(
                            index=device_index,
                            name=f"{display_name} [System Audio Output]",
                            device_id=f"wasapi:{i}",  # Store PyAudio device index
                            device_type="output",
                        )
                    )
                    device_index += 1

            p.terminate()
            logger.info(f"Found {len(devices)} WASAPI loopback devices")

        except ImportError:
            logger.warning(
                "pyaudiowpatch not available, WASAPI loopback devices not enumerated"
            )
        except Exception as e:
            logger.error(f"Error enumerating WASAPI loopback devices: {e}")

        # Also enumerate DirectShow devices (microphones, Stereo Mix if enabled)
        try:
            result = subprocess.run(
                ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Parse DirectShow devices
            for line in result.stderr.split("\n"):
                if "(audio)" in line and '"' in line:
                    match = re.search(r'"([^"]+)"\s*\(audio\)', line)
                    if match:
                        device_name = match.group(1)
                        # Detect if this is Stereo Mix
                        is_stereo_mix = any(
                            keyword in device_name.lower()
                            for keyword in ["stereo mix", "wave out", "what u hear"]
                        )

                        devices.append(
                            AudioDevice(
                                index=device_index,
                                name=f"{device_name}"
                                + (
                                    " [System Audio]"
                                    if is_stereo_mix
                                    else " [Microphone]"
                                ),
                                device_id=f"dshow:audio={device_name}",
                                device_type="output" if is_stereo_mix else "input",
                            )
                        )
                        device_index += 1

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg and add it to your PATH."
            )
        except subprocess.TimeoutExpired:
            logger.warning("FFmpeg device enumeration timed out")
        except Exception as e:
            logger.error(f"Failed to enumerate DirectShow devices: {e}")

        if not devices:
            logger.warning("No audio devices found on Windows")

        return devices

    @staticmethod
    def _enumerate_linux_devices() -> List[AudioDevice]:
        """Enumerate audio devices on Linux using ALSA/PulseAudio.

        Returns:
            List of available audio devices.

        Raises:
            RuntimeError: If FFmpeg is not available.
        """
        try:
            # Try PulseAudio first
            result = subprocess.run(
                ["ffmpeg", "-sources", "pulse"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            devices = []
            device_index = 1

            # Parse output
            for line in result.stderr.split("\n"):
                if "* " in line:  # PulseAudio device line
                    device_name = line.split("* ")[1].strip()
                    devices.append(
                        AudioDevice(
                            index=device_index,
                            name=device_name,
                            device_id=device_name,
                            device_type="input",
                        )
                    )
                    device_index += 1

            # If no PulseAudio devices, try ALSA
            if not devices:
                result = subprocess.run(
                    ["arecord", "-L"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                for line in result.stdout.split("\n"):
                    line = line.strip()
                    if line and not line.startswith(" "):
                        devices.append(
                            AudioDevice(
                                index=device_index,
                                name=line,
                                device_id=line,
                                device_type="input",
                            )
                        )
                        device_index += 1

            return devices

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg or audio tools not found. Please install FFmpeg and ALSA/PulseAudio utilities."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to enumerate Linux audio devices: {e}")

    @staticmethod
    def _enumerate_macos_devices() -> List[AudioDevice]:
        """Enumerate audio devices on macOS using AVFoundation.

        Returns:
            List of available audio devices.

        Raises:
            RuntimeError: If FFmpeg is not available.
        """
        try:
            # Run FFmpeg to list AVFoundation devices
            result = subprocess.run(
                ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
                capture_output=True,
                text=True,
                timeout=10,
            )

            devices = []
            device_index = 1

            # Parse audio input devices from stderr
            in_audio_section = False
            for line in result.stderr.split("\n"):
                if "AVFoundation audio devices:" in line:
                    in_audio_section = True
                    continue
                elif "AVFoundation video devices:" in line:
                    in_audio_section = False
                    continue

                if in_audio_section and "]" in line:
                    # Extract device name
                    match = re.search(r"\[.*?\]\s+\[\d+\]\s+(.+)", line)
                    if match:
                        device_name = match.group(1).strip()
                        devices.append(
                            AudioDevice(
                                index=device_index,
                                name=device_name,
                                device_id=f":{device_index - 1}",
                                device_type="input",
                            )
                        )
                        device_index += 1

            return devices

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg and add it to your PATH."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to enumerate macOS audio devices: {e}")

    @staticmethod
    def get_device_by_index(index: int) -> Optional[AudioDevice]:
        """Get audio device by index.

        Args:
            index: Device index (1-based).

        Returns:
            AudioDevice if found, None otherwise.
        """
        devices = AudioDeviceEnumerator.enumerate_devices()
        for device in devices:
            if device.index == index:
                return device
        return None

    @staticmethod
    def display_devices() -> None:
        """Display available audio devices to console."""
        devices = AudioDeviceEnumerator.enumerate_devices()

        if not devices:
            print("No audio devices found.")
            return

        print("\n=== Available Audio Devices ===")
        for device in devices:
            print(f"{device.index}. {device.name}")
        print()
