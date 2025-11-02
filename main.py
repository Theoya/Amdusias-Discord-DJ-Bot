"""Main entry point for the Discord DJ Bot."""

import asyncio
import logging
import sys
from typing import Optional
from src.config import ConfigLoader, AudioSourceConfig, BotConfig
from src.bot import DJBot
from src.audio_device import AudioDeviceEnumerator, AudioDevice
from src.audio_source_factory import AudioSourceFactory


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log')
        ]
    )


def select_audio_source(config: BotConfig) -> AudioSourceConfig:
    """Display audio source selection menu and get user choice.

    Args:
        config: Bot configuration.

    Returns:
        Selected audio source configuration.
    """
    print("\n" + "=" * 60)
    print("  Amdusias Discord DJ Bot - Audio Source Selection")
    print("=" * 60)

    # Get available local devices
    try:
        devices = AudioDeviceEnumerator.enumerate_devices()
    except RuntimeError as e:
        print(f"\nWarning: Could not enumerate local audio devices: {e}")
        devices = []

    # Build menu options
    menu_options = []
    option_num = 1

    # Add local devices
    if devices:
        print("\nLocal Audio Devices:")
        for device in devices:
            print(f"  {option_num}. {device.name}")
            menu_options.append(("local", device))
            option_num += 1

    # Add custom URL option
    print(f"  {option_num}. Custom URL Stream")
    menu_options.append(("url", None))

    if not menu_options:
        print("\nNo audio sources available!")
        print("Please check your configuration or install FFmpeg.")
        sys.exit(1)

    # Get user selection
    print("\n" + "=" * 60)
    while True:
        try:
            selection = input("Select audio source (enter number): ").strip()
            choice_num = int(selection)

            if 1 <= choice_num <= len(menu_options):
                source_type, source_data = menu_options[choice_num - 1]

                if source_type == "local":
                    device = source_data
                    return AudioSourceConfig(
                        source_type="local",
                        device_index=device.index,
                        bitrate=config.audio.bitrate,
                        sample_rate=config.audio.sample_rate,
                    )

                elif source_type == "url":
                    url = input("Enter stream URL: ").strip()
                    if not url:
                        print("URL cannot be empty!")
                        continue
                    return AudioSourceConfig(
                        source_type="url",
                        url=url,
                        bitrate=config.audio.bitrate,
                    )

            else:
                print(f"Please enter a number between 1 and {len(menu_options)}")

        except ValueError:
            print("Invalid input! Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nSelection cancelled by user.")
            sys.exit(0)


async def main() -> None:
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Loading configuration...")
        config = ConfigLoader.load_config()

        # Select audio source via CLI menu
        print("\n")
        audio_source_config = select_audio_source(config)
        config.audio_source = audio_source_config

        # Create the audio source
        source = AudioSourceFactory.create_from_config(
            source_type=audio_source_config.source_type,
            config={
                "device_index": audio_source_config.device_index,
                "url": audio_source_config.url,
                "bitrate": audio_source_config.bitrate,
                "sample_rate": audio_source_config.sample_rate,
            }
        )

        print(f"\n✓ Selected: {source.get_description()}")
        print("=" * 60)

        logger.info("Initializing bot...")
        bot = DJBot(config, audio_source=source)

        logger.info("Starting bot...")
        async with bot:
            await bot.start(config.discord.token)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested by user")
