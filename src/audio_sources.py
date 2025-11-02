"""Audio source implementations for different streaming sources."""

import logging
from typing import Protocol, Optional, Dict, Any
from enum import Enum
import discord
import subprocess
import threading
import io
from src.audio_device import AudioDevice


logger = logging.getLogger(__name__)


class AudioSourceType(Enum):
    """Types of audio sources supported by the bot."""

    LOCAL_DEVICE = "local_device"
    ICECAST_STREAM = "icecast_stream"
    URL_STREAM = "url_stream"
    FILE = "file"
    WASAPI_LOOPBACK = "wasapi_loopback"


class AudioSourceProtocol(Protocol):
    """Protocol defining the interface for all audio sources.

    This protocol ensures all audio sources can be used interchangeably
    and provides a consistent interface for the bot.
    """

    def get_type(self) -> AudioSourceType:
        """Get the type of this audio source.

        Returns:
            AudioSourceType enum value.
        """
        ...

    def get_description(self) -> str:
        """Get a human-readable description of this audio source.

        Returns:
            Description string.
        """
        ...

    def create_discord_source(self) -> discord.AudioSource:
        """Create a Discord audio source for playback.

        Returns:
            Discord-compatible audio source.

        Raises:
            RuntimeError: If source creation fails.
        """
        ...

    def cleanup(self) -> None:
        """Clean up any resources used by this audio source."""
        ...


class LocalAudioSource:
    """Audio source that captures from a local audio device."""

    def __init__(self, device: AudioDevice, sample_rate: int = 48000, bitrate: int = 128) -> None:
        """Initialize local audio source.

        Args:
            device: Audio device to capture from.
            sample_rate: Audio sample rate in Hz (default 48000).
            bitrate: Audio bitrate in kbps (default 128).
        """
        self._device = device
        self._sample_rate = sample_rate
        self._bitrate = bitrate
        self._platform = device.device_type

    def get_type(self) -> AudioSourceType:
        """Get the type of this audio source.

        Returns:
            AudioSourceType.LOCAL_DEVICE
        """
        return AudioSourceType.LOCAL_DEVICE

    def get_description(self) -> str:
        """Get a human-readable description of this audio source.

        Returns:
            Description string.
        """
        return f"Local Device: {self._device.name}"

    def create_discord_source(self) -> discord.AudioSource:
        """Create a Discord audio source for playback.

        Returns:
            Discord FFmpegPCMAudio source configured for the local device.

        Raises:
            RuntimeError: If FFmpeg fails to connect to the device.
        """
        try:
            # Build FFmpeg input format based on platform
            input_format = self._get_input_format()
            input_device = self._get_input_device()

            # FFmpeg options for local device capture
            before_options = f"-f {input_format}"

            # Output options for Discord
            # -ar: sample rate, -ac: channels (2=stereo), -b:a: bitrate
            options = f"-ar {self._sample_rate} -ac 2 -b:a {self._bitrate}k"

            logger.info(f"Creating audio source from device: {self._device.name}")
            logger.debug(f"FFmpeg input: {input_format} {input_device}")
            logger.debug(f"FFmpeg options: before={before_options}, after={options}")

            return discord.FFmpegPCMAudio(
                input_device,
                before_options=before_options,
                options=options,
            )

        except Exception as e:
            logger.error(f"Failed to create local audio source: {e}")
            raise RuntimeError(f"Failed to connect to audio device '{self._device.name}': {e}")

    def _get_input_format(self) -> str:
        """Get the FFmpeg input format for the current platform.

        Returns:
            FFmpeg input format string.
        """
        import platform

        system = platform.system().lower()

        if system == "windows":
            return "dshow"
        elif system == "linux":
            return "pulse"  # or 'alsa' as fallback
        elif system == "darwin":
            return "avfoundation"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def _get_input_device(self) -> str:
        """Get the FFmpeg input device string.

        Returns:
            Device string formatted for FFmpeg.
        """
        # Special handling for desktop audio (system output capture)
        if self._device.device_id == "desktop-audio":
            # Use audio loopback - captures default playback device
            import platform
            if platform.system().lower() == "windows":
                # For Windows, we'll use dshow with a loopback device or
                # try to use the default audio renderer
                return "audio=@device_cm_{33D9A762-90C8-11D0-BD43-00A0C911CE86}\\wave_{00000000-0000-0000-0000-000000000000}"

        return self._device.device_id

    def cleanup(self) -> None:
        """Clean up any resources used by this audio source."""
        logger.debug(f"Cleaning up local audio source: {self._device.name}")
        # No specific cleanup needed for FFmpeg-based sources
        pass


class IcecastAudioSource:
    """Audio source that streams from an Icecast server."""

    def __init__(self, url: str, bitrate: int = 128) -> None:
        """Initialize Icecast audio source.

        Args:
            url: Icecast stream URL.
            bitrate: Audio bitrate in kbps (default 128).
        """
        self._url = url
        self._bitrate = bitrate

    def get_type(self) -> AudioSourceType:
        """Get the type of this audio source.

        Returns:
            AudioSourceType.ICECAST_STREAM
        """
        return AudioSourceType.ICECAST_STREAM

    def get_description(self) -> str:
        """Get a human-readable description of this audio source.

        Returns:
            Description string.
        """
        return f"Icecast Stream: {self._url}"

    def create_discord_source(self) -> discord.AudioSource:
        """Create a Discord audio source for playback.

        Returns:
            Discord FFmpegPCMAudio source configured for Icecast streaming.

        Raises:
            RuntimeError: If FFmpeg fails to connect to the stream.
        """
        try:
            # FFmpeg options for better streaming stability
            before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

            # Output options for Discord
            options = f"-vn -b:a {self._bitrate}k"

            logger.info(f"Creating audio source from Icecast: {self._url}")

            return discord.FFmpegPCMAudio(
                self._url,
                before_options=before_options,
                options=options,
            )

        except Exception as e:
            logger.error(f"Failed to create Icecast audio source: {e}")
            raise RuntimeError(f"Failed to connect to Icecast stream '{self._url}': {e}")

    def cleanup(self) -> None:
        """Clean up any resources used by this audio source."""
        logger.debug(f"Cleaning up Icecast audio source: {self._url}")
        # No specific cleanup needed for FFmpeg-based sources
        pass


class URLAudioSource:
    """Audio source that streams from any URL (YouTube, SoundCloud, etc.)."""

    def __init__(self, url: str, bitrate: int = 128) -> None:
        """Initialize URL audio source.

        Args:
            url: Stream URL.
            bitrate: Audio bitrate in kbps (default 128).
        """
        self._url = url
        self._bitrate = bitrate

    def get_type(self) -> AudioSourceType:
        """Get the type of this audio source.

        Returns:
            AudioSourceType.URL_STREAM
        """
        return AudioSourceType.URL_STREAM

    def get_description(self) -> str:
        """Get a human-readable description of this audio source.

        Returns:
            Description string.
        """
        return f"URL Stream: {self._url}"

    def create_discord_source(self) -> discord.AudioSource:
        """Create a Discord audio source for playback.

        Returns:
            Discord FFmpegPCMAudio source configured for URL streaming.

        Raises:
            RuntimeError: If FFmpeg fails to connect to the URL.
        """
        try:
            # FFmpeg options for streaming
            before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            options = f"-vn -b:a {self._bitrate}k"

            logger.info(f"Creating audio source from URL: {self._url}")

            return discord.FFmpegPCMAudio(
                self._url,
                before_options=before_options,
                options=options,
            )

        except Exception as e:
            logger.error(f"Failed to create URL audio source: {e}")
            raise RuntimeError(f"Failed to connect to URL '{self._url}': {e}")

    def cleanup(self) -> None:
        """Clean up any resources used by this audio source."""
        logger.debug(f"Cleaning up URL audio source: {self._url}")
        pass


class WASAPILoopbackPCMAudio(discord.AudioSource):
    """Custom Discord AudioSource that reads from WASAPI loopback."""

    def __init__(self, device_index: int, device_name: str, sample_rate: int, channels: int):
        """Initialize WASAPI PCM audio source.

        Args:
            device_index: PyAudio device index.
            device_name: Name of the audio device.
            sample_rate: Device sample rate.
            channels: Number of audio channels.
        """
        import pyaudiowpatch as pyaudio
        import audioop

        self._device_index = device_index
        self._device_name = device_name
        self._sample_rate = sample_rate
        self._channels = channels
        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._buffer = b''

        # Open audio stream
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=self._channels,
            rate=self._sample_rate,
            frames_per_buffer=960,  # 20ms at 48kHz
            input=True,
            input_device_index=self._device_index,
        )

        logger.info(f"WASAPI loopback stream opened: {self._device_name}")

    def read(self) -> bytes:
        """Read 20ms of audio data.

        Discord expects 3840 bytes per frame (20ms at 48kHz stereo 16-bit).

        Returns:
            Audio data as bytes.
        """
        try:
            if not self._stream or not self._stream.is_active():
                return b''

            # Read from PyAudio stream
            # Need to read enough for 20ms at the device's sample rate
            frames_needed = int(self._sample_rate * 0.02)  # 20ms worth of frames
            data = self._stream.read(frames_needed, exception_on_overflow=False)

            # Resample if needed
            if self._sample_rate != 48000:
                import audioop
                data, _ = audioop.ratecv(
                    data,
                    2,  # 16-bit = 2 bytes
                    self._channels,
                    self._sample_rate,
                    48000,
                    None
                )

            # Convert to stereo if mono
            if self._channels == 1:
                import audioop
                data = audioop.tostereo(data, 2, 1, 1)

            return data

        except Exception as e:
            logger.error(f"Error reading from WASAPI loopback: {e}")
            return b''

    def cleanup(self):
        """Clean up audio stream resources."""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            logger.info("WASAPI loopback stream closed")

        if self._pyaudio:
            self._pyaudio.terminate()


class WASAPILoopbackAudioSource:
    """Audio source that captures system audio using WASAPI loopback."""

    def __init__(self, device_index: int, sample_rate: int = 48000, bitrate: int = 128) -> None:
        """Initialize WASAPI loopback audio source.

        Args:
            device_index: PyAudio device index for the loopback device.
            sample_rate: Audio sample rate in Hz (default 48000).
            bitrate: Audio bitrate in kbps (default 128).
        """
        self._device_index = device_index
        self._sample_rate = sample_rate
        self._bitrate = bitrate
        self._device_name = "Unknown Device"

        # Get device info
        try:
            import pyaudiowpatch as pyaudio
            p = pyaudio.PyAudio()
            info = p.get_device_info_by_index(device_index)
            self._device_name = info['name'].replace(' [Loopback]', '')
            self._device_sample_rate = int(info['defaultSampleRate'])
            self._device_channels = info['maxInputChannels']
            p.terminate()
        except Exception as e:
            logger.warning(f"Could not get device info: {e}")
            self._device_sample_rate = 48000
            self._device_channels = 2

    def get_type(self) -> AudioSourceType:
        """Get the type of this audio source.

        Returns:
            AudioSourceType.WASAPI_LOOPBACK
        """
        return AudioSourceType.WASAPI_LOOPBACK

    def get_description(self) -> str:
        """Get a human-readable description of this audio source.

        Returns:
            Description string.
        """
        return f"System Audio: {self._device_name}"

    def create_discord_source(self) -> discord.AudioSource:
        """Create a Discord audio source for playback.

        Returns:
            Discord audio source that captures from WASAPI loopback.

        Raises:
            RuntimeError: If audio capture fails.
        """
        try:
            logger.info(f"Creating WASAPI loopback source: {self._device_name}")
            logger.debug(f"Device index: {self._device_index}, Sample rate: {self._device_sample_rate}, Channels: {self._device_channels}")

            # Create custom PCM audio source
            return WASAPILoopbackPCMAudio(
                device_index=self._device_index,
                device_name=self._device_name,
                sample_rate=self._device_sample_rate,
                channels=self._device_channels,
            )

        except ImportError:
            raise RuntimeError("pyaudiowpatch not installed - cannot use WASAPI loopback")
        except Exception as e:
            logger.error(f"Failed to create WASAPI loopback source: {e}")
            raise RuntimeError(f"Failed to capture system audio: {e}")

    def cleanup(self) -> None:
        """Clean up any resources used by this audio source."""
        logger.debug(f"Cleaning up WASAPI loopback source: {self._device_name}")
