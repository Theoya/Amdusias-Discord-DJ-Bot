# Quick Start Guide

Get your Discord DJ bot streaming in 5 steps!

## Step 1: Install Prerequisites

### Windows
- Python 3.10+: Download from [python.org](https://www.python.org/downloads/)
- FFmpeg: Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, add to PATH
- Icecast2: Download from [icecast.org](https://icecast.org/download/)
- VB-Audio Cable: Download from [vb-audio.com](https://vb-audio.com/Cable/)

### Linux
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv ffmpeg icecast2
```

## Step 2: Set Up Python Environment

```bash
# Clone the repo
git clone https://github.com/yourusername/Amdusias-Discord-DJ-Bot.git
cd Amdusias-Discord-DJ-Bot

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Icecast

Edit Icecast configuration:
- Windows: `C:\Program Files (x86)\Icecast2 Win32\icecast.xml`
- Linux: `/etc/icecast2/icecast.xml`

Change passwords and hostname:
```xml
<source-password>YourStrongPasswordHere</source-password>
<hostname>your-public-ip-or-hostname</hostname>
```

Start Icecast:
- Windows: Services → Icecast2win → Start
- Linux: `sudo systemctl start icecast2`

Verify: Open `http://localhost:8000` in browser

## Step 4: Set Up Audio Routing

### Install Virtual Cable
1. Install VB-Audio Cable
2. Set DJ software output to "CABLE Input"
3. Install BUTT encoder from [danielnoethen.de/butt](https://danielnoethen.de/butt/)

### Configure BUTT
- Audio Device: CABLE Output
- Server: 127.0.0.1
- Port: 8000
- Password: Your source password from Step 3
- Mount: /live
- Codec: MP3, 128 kbps

Click "Play" in BUTT to start streaming.

## Step 5: Configure and Run Bot

### Create Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Go to Bot → Add Bot
4. Enable "Message Content Intent"
5. Copy bot token
6. Go to OAuth2 → URL Generator
   - Scopes: bot
   - Permissions: Connect, Speak
7. Use URL to invite bot to your server

### Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env (Windows: notepad .env, Linux: nano .env)
# Add your bot token and public IP
```

Required in `.env`:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
ICECAST_URL=http://YOUR_PUBLIC_IP:8000/live
```

### Port Forward (if needed)
Configure router to forward port 8000 TCP to your PC's local IP.

### Run the Bot
```bash
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh
```

## Using the Bot

In Discord:
```
!join   - Join your voice channel
!play   - Start streaming
!stop   - Stop streaming
!leave  - Leave voice channel
```

## Typical Session

1. Start Icecast server
2. Start BUTT encoder (click Play)
3. Run bot: `python main.py`
4. Join Discord voice channel
5. Type `!join`
6. Type `!play`
7. Start mixing in your DJ software!

## Troubleshooting

### Bot won't start
- Check `.env` file exists and has correct token
- Verify Python 3.10+ installed: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt`

### No audio in Discord
- Verify BUTT is streaming (green indicator)
- Check Icecast status at `http://localhost:8000`
- Ensure FFmpeg is in PATH: `ffmpeg -version`
- Try `!stop` then `!play`

### Can't connect from outside
- Verify port forwarding: port 8000 to your PC
- Check firewall allows port 8000
- Use your public IP in `ICECAST_URL`
- Find public IP: [whatismyip.com](https://www.whatismyip.com/)

## Testing

Run tests to verify everything works:
```bash
pytest
```

Should see all tests passing.

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Read [CLAUDE.md](CLAUDE.md) for development guidelines
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Support

- Open an issue on GitHub
- Check existing issues for solutions
- See full [README.md](README.md) for detailed troubleshooting

---

**Happy DJing!**
