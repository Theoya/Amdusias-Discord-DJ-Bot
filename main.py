"""Main entry point for the Discord DJ Bot."""

import asyncio
import logging
import sys
from src.config import ConfigLoader
from src.bot import DJBot


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


async def main() -> None:
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Loading configuration...")
        config = ConfigLoader.load_config()

        logger.info("Initializing bot...")
        bot = DJBot(config)

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
