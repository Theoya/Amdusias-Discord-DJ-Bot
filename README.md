# Amdusias Discord DJ Bot

A streamlined Discord bot for DJs to stream live audio to friends using Icecast and Discord voice channels.

## Overview

This bot allows you to stream audio from your DJ software (Serato, Rekordbox, VirtualDJ, etc.) to your friends on Discord. It works by:

1. Capturing audio output from your DJ software
2. Encoding and streaming to an Icecast server on your PC
3. The Discord bot reads from the Icecast stream
4. Broadcasting to Discord voice channels

### Bandwidth Considerations

Each Discord listener receives their own unicast stream. Your uplink bandwidth is the limiting factor:

```
Max listeners ≈ (uplink_Mbps × 1000) / (audio_kbps × 1.1)
```

**Example**: 20 Mbps uplink at 128 kbps = ~142 simultaneous listeners

## Features

- Stream live DJ audio to Discord voice channels
- Simple bot commands (!join, !play, !stop, !leave)
- Automatic reconnection to stream on failure
- Full test coverage with unit tests
- Type-safe Python code with mypy
- CI/CD with GitHub Actions

## Architecture

```
DJ Software → Virtual Audio → Encoder → Icecast → Discord Bot → Voice Channel → Friends
```

See [architecture.mermaid](architecture.mermaid) for detailed diagram.

## Prerequisites

### Software Requirements

- Python 3.10 or higher
- FFmpeg (for audio processing)
- Icecast2 server
- Virtual audio cable (VB-Audio Cable, Stereo Mix, or similar)
- Audio encoding software (BUTT, FFmpeg, or OBS)

### Network Requirements

- Public IP or dynamic DNS
- Port forwarding on your router (port 8000 TCP)
- Or use a tunnel service like ngrok if behind CG-NAT

### Discord Requirements

- Discord bot token ([Create one here](https://discord.com/developers/applications))
- Bot must have:
  - Voice permissions
  - Message content intent enabled

## Installation

### 1. Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/Amdusias-Discord-DJ-Bot.git
cd Amdusias-Discord-DJ-Bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows**:
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract and add to PATH

**Linux**:
```bash
sudo apt-get install ffmpeg
```

**Mac**:
```bash
brew install ffmpeg
```

### 3. Install and Configure Icecast

**Windows**:
1. Download [Icecast2 for Windows](https://icecast.org/download/)
2. Install to `C:\Program Files (x86)\Icecast2 Win32\`
3. Edit `C:\Program Files (x86)\Icecast2 Win32\icecast.xml`:

```xml
<icecast>
  <location>Home</location>
  <admin>you@example.com</admin>

  <limits>
    <clients>512</clients>
    <sources>4</sources>
    <queue-size>524288</queue-size>
    <burst-size>65535</burst-size>
  </limits>

  <authentication>
    <source-password>ChangeThisSourcePassword123!</source-password>
    <relay-password>ChangeThisRelayPassword123!</relay-password>
    <admin-user>admin</admin-user>
    <admin-password>ChangeThisAdminPassword123!</admin-password>
  </authentication>

  <hostname>your.public.ip.or.hostname</hostname>
  <listen-socket>
    <port>8000</port>
  </listen-socket>

  <fileserve>1</fileserve>
  <paths>
    <basedir>./</basedir>
    <logdir>./logs</logdir>
    <webroot>./web</webroot>
    <adminroot>./admin</adminroot>
    <alias source="/" dest="/status.xsl"/>
  </paths>

  <logging>
    <accesslog>access.log</accesslog>
    <errorlog>error.log</errorlog>
    <loglevel>3</loglevel>
  </logging>
</icecast>
```

4. Start Icecast service (Services → Icecast2win → Start)
5. Verify at `http://127.0.0.1:8000`

**Linux**:
```bash
sudo apt-get install icecast2
sudo nano /etc/icecast2/icecast.xml
# Configure as above
sudo systemctl start icecast2
sudo systemctl enable icecast2
```

### 4. Configure Audio Routing

#### Option A: Virtual Audio Cable (Recommended)

1. Install [VB-Audio Cable](https://vb-audio.com/Cable/)
2. Set your DJ software's audio output to "CABLE Input"
3. Configure encoder to capture from "CABLE Output"

#### Option B: Stereo Mix (Windows)

1. Right-click sound icon → Sounds → Recording
2. Enable "Stereo Mix"
3. Configure encoder to capture from "Stereo Mix"

### 5. Configure Audio Encoder

#### Option A: BUTT (Broadcast Using This Tool) - Easiest

1. Download [BUTT](https://danielnoethen.de/butt/)
2. Configure:
   - Settings → Audio
     - Audio Device: Select your virtual cable output
   - Settings → Server
     - Type: Icecast
     - Address: 127.0.0.1
     - Port: 8000
     - Password: Your source password from icecast.xml
     - Mount: /live
   - Settings → Codec
     - Codec: MP3
     - Bitrate: 128 kbps
3. Click "Play" to start streaming

#### Option B: FFmpeg Command Line

```bash
# Windows (with virtual cable)
ffmpeg -f dshow -i audio="CABLE Output (VB-Audio Virtual Cable)" ^
  -c:a libmp3lame -b:a 128k -content_type audio/mpeg -f mp3 ^
  icecast://source:YourSourcePassword@127.0.0.1:8000/live

# Linux (with PulseAudio)
ffmpeg -f pulse -i default ^
  -c:a libmp3lame -b:a 128k -content_type audio/mpeg -f mp3 ^
  icecast://source:YourSourcePassword@127.0.0.1:8000/live
```

### 6. Configure Port Forwarding

1. Log into your router admin panel
2. Forward external port 8000 TCP → your PC's local IP:8000
3. Find your public IP at [whatismyip.com](https://www.whatismyip.com/)

**Alternative**: Use ngrok if behind CG-NAT:
```bash
ngrok tcp 8000
```

### 7. Configure Discord Bot

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Go to "Bot" section
3. Click "Add Bot"
4. Enable "Message Content Intent" under "Privileged Gateway Intents"
5. Copy the bot token
6. Go to OAuth2 → URL Generator
   - Scopes: `bot`
   - Bot Permissions: `Connect`, `Speak`, `Use Voice Activity`
7. Use generated URL to invite bot to your server

### 8. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Windows: notepad .env
# Linux/Mac: nano .env
```

Required configuration in `.env`:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here  # Optional

# Icecast Server Configuration
ICECAST_HOST=127.0.0.1
ICECAST_PORT=8000
ICECAST_MOUNT=/live
ICECAST_URL=http://YOUR_PUBLIC_IP:8000/live  # Use your public IP

# Audio Configuration
AUDIO_BITRATE=128
AUDIO_SAMPLE_RATE=48000

# Bot Configuration
COMMAND_PREFIX=!
```

## Usage

### Starting the Bot

```bash
# Activate virtual environment if not already active
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run the bot
python main.py
```

You should see:
```
INFO - Loading configuration...
INFO - Initializing bot...
INFO - Starting bot...
INFO - Bot logged in as YourBotName#1234
```

### Discord Commands

Once the bot is running and in your Discord server:

```
!join   - Bot joins your current voice channel
!play   - Start streaming audio from Icecast
!stop   - Stop streaming audio
!leave  - Bot leaves the voice channel
```

### Typical Workflow

1. Start Icecast server
2. Start audio encoder (BUTT/FFmpeg)
3. Start the Discord bot: `python main.py`
4. In Discord, join a voice channel
5. Type `!join` - bot joins your channel
6. Type `!play` - bot starts streaming
7. Start your DJ software and mix
8. Friends can join the voice channel to listen

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# View coverage report
# Windows:
start htmlcov/index.html
# Linux/Mac:
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src tests

# Check types
mypy src

# Lint code
flake8 src tests
```

### Pre-Commit Checks

Before committing, ensure:
```bash
black src tests
mypy src
flake8 src tests
pytest --cov=src
```

See [CLAUDE.md](CLAUDE.md) for complete development guidelines.

## Troubleshooting

### Bot won't connect to Icecast

- Verify Icecast is running: `http://127.0.0.1:8000`
- Check `ICECAST_URL` in `.env` matches your public IP
- Verify port forwarding is configured correctly
- Check firewall allows port 8000

### No audio in Discord

- Verify audio encoder is streaming to Icecast
- Check Icecast status page shows active source
- Ensure FFmpeg is installed and in PATH
- Try stopping and starting the stream: `!stop` then `!play`

### Bot crashes on startup

- Verify all environment variables in `.env` are set
- Check Discord bot token is valid
- Ensure Python 3.10+ is installed
- Verify all dependencies installed: `pip install -r requirements.txt`

### Audio quality issues

- Increase bitrate in encoder (try 192 kbps)
- Check for CPU/network bottlenecks
- Verify adequate upload bandwidth
- Reduce number of simultaneous listeners

### Bot commands not working

- Verify bot has proper permissions in Discord server
- Check "Message Content Intent" is enabled in Discord Developer Portal
- Ensure bot is using correct command prefix (default: `!`)

## Project Structure

```
Amdusias-Discord-DJ-Bot/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── stream_reader.py    # Icecast stream reader
│   ├── audio_source.py     # Discord audio source adapter
│   └── bot.py              # Discord bot implementation
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_stream_reader.py
│   ├── test_audio_source.py
│   └── test_bot.py
├── .github/
│   └── workflows/
│       └── tests.yml       # CI/CD pipeline
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore
├── pytest.ini             # Pytest configuration
├── mypy.ini              # Type checking configuration
├── CLAUDE.md             # Development best practices
├── architecture.mermaid  # Architecture diagram
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Ensure all tests pass: `pytest`
5. Ensure code quality: `black src tests && mypy src && flake8 src tests`
6. Commit changes: `git commit -m "feat: add my feature"`
7. Push to branch: `git push origin feature/my-feature`
8. Create a Pull Request

All PRs must:
- Pass all tests
- Maintain 80%+ code coverage
- Pass type checking
- Pass linting
- Follow code style guidelines

See [CLAUDE.md](CLAUDE.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Audio streaming via [Icecast](https://icecast.org/)
- Audio processing with [FFmpeg](https://ffmpeg.org/)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- See [CLAUDE.md](CLAUDE.md) for development guidelines

## Roadmap

Future enhancements:
- [ ] Web dashboard for monitoring listeners
- [ ] Multiple stream quality options
- [ ] Playlist management
- [ ] Recorded session archiving
- [ ] Listener statistics and analytics
- [ ] Support for multiple simultaneous channels

---

**Made with love for DJs streaming to friends on Discord**
