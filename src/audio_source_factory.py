"""Factory for creating audio sources based on configuration."""

import logging
from typing import Optional, Union
from src.audio_sources import (
    AudioSourceProtocol,
    LocalAudioSource,
    IcecastAudioSource,
    URLAudioSource,
    WASAPILoopbackAudioSource,
    AudioSourceType,
)
from src.audio_device import AudioDevice, AudioDeviceEnumerator


logger = logging.getLogger(__name__)


class AudioSourceFactory:
    """Factory for creating different types of audio sources."""

    @staticmethod
    def create_local_source(
        device: AudioDevice,
        sample_rate: int = 48000,
        bitrate: int = 128,
    ) -> LocalAudioSource:
        """Create a local audio device source.

        Args:
            device: Audio device to use.
            sample_rate: Sample rate in Hz.
            bitrate: Bitrate in kbps.

        Returns:
            LocalAudioSource instance.
        """
        logger.info(f"Creating local audio source for device: {device.name}")
        return LocalAudioSource(device=device, sample_rate=sample_rate, bitrate=bitrate)

    @staticmethod
    def create_local_source_by_index(
        device_index: int,
        sample_rate: int = 48000,
        bitrate: int = 128,
    ) -> Union[LocalAudioSource, WASAPILoopbackAudioSource]:
        """Create a local audio device source by device index.

        Args:
            device_index: Device index (1-based).
            sample_rate: Sample rate in Hz.
            bitrate: Bitrate in kbps.

        Returns:
            LocalAudioSource or WASAPILoopbackAudioSource instance.

        Raises:
            ValueError: If device index is invalid.
        """
        device = AudioDeviceEnumerator.get_device_by_index(device_index)
        if device is None:
            raise ValueError(f"No audio device found with index {device_index}")

        # Check if this is a WASAPI loopback device
        if device.device_id.startswith("wasapi:"):
            # Extract PyAudio device index from device_id
            pyaudio_index = int(device.device_id.split(":")[1])
            return WASAPILoopbackAudioSource(
                device_index=pyaudio_index,
                sample_rate=sample_rate,
                bitrate=bitrate,
            )
        else:
            return AudioSourceFactory.create_local_source(
                device=device,
                sample_rate=sample_rate,
                bitrate=bitrate,
            )

    @staticmethod
    def create_icecast_source(
        url: str,
        bitrate: int = 128,
    ) -> IcecastAudioSource:
        """Create an Icecast stream source.

        Args:
            url: Icecast stream URL.
            bitrate: Bitrate in kbps.

        Returns:
            IcecastAudioSource instance.
        """
        logger.info(f"Creating Icecast audio source for URL: {url}")
        return IcecastAudioSource(url=url, bitrate=bitrate)

    @staticmethod
    def create_url_source(
        url: str,
        bitrate: int = 128,
    ) -> URLAudioSource:
        """Create a URL stream source.

        Args:
            url: Stream URL.
            bitrate: Bitrate in kbps.

        Returns:
            URLAudioSource instance.
        """
        logger.info(f"Creating URL audio source for: {url}")
        return URLAudioSource(url=url, bitrate=bitrate)

    @staticmethod
    def create_from_config(
        source_type: str,
        config: dict,
    ) -> Union[LocalAudioSource, IcecastAudioSource, URLAudioSource]:
        """Create an audio source from configuration.

        Args:
            source_type: Type of source ('local', 'icecast', 'url').
            config: Configuration dictionary.

        Returns:
            Audio source instance.

        Raises:
            ValueError: If source type is invalid or configuration is missing required fields.
        """
        source_type_lower = source_type.lower()

        if source_type_lower == "local":
            device_index = config.get("device_index")
            if device_index is None:
                raise ValueError("Local audio source requires 'device_index' in config")

            return AudioSourceFactory.create_local_source_by_index(
                device_index=device_index,
                sample_rate=config.get("sample_rate", 48000),
                bitrate=config.get("bitrate", 128),
            )

        elif source_type_lower == "icecast":
            url = config.get("url")
            if url is None:
                raise ValueError("Icecast audio source requires 'url' in config")

            return AudioSourceFactory.create_icecast_source(
                url=url,
                bitrate=config.get("bitrate", 128),
            )

        elif source_type_lower == "url":
            url = config.get("url")
            if url is None:
                raise ValueError("URL audio source requires 'url' in config")

            return AudioSourceFactory.create_url_source(
                url=url,
                bitrate=config.get("bitrate", 128),
            )

        else:
            raise ValueError(
                f"Unknown audio source type: {source_type}. "
                f"Expected 'local', 'icecast', or 'url'"
            )
