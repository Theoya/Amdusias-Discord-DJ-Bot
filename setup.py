"""Setup script for Amdusias Discord DJ Bot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amdusias-discord-dj-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Discord bot for DJs to stream live audio via Icecast",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Amdusias-Discord-DJ-Bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "discord.py[voice]==2.3.2",
        "PyNaCl==1.5.0",
        "python-dotenv==1.0.0",
        "ffmpeg-python==0.2.0",
        "requests==2.31.0",
        "aiohttp==3.9.1",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0",
            "pytest-mock==3.12.0",
            "black==23.12.1",
            "flake8==6.1.0",
            "mypy==1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "amdusias-bot=main:main",
        ],
    },
)
