"""Test script to verify audio capture is working."""

import subprocess
import sys

print("=" * 60)
print("Audio Capture Test")
print("=" * 60)

# List all audio devices
print("\n1. Listing available audio devices...\n")
result = subprocess.run(
    ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
    capture_output=True,
    text=True,
)

# Show only audio devices
print("Available Audio Input Devices:")
for line in result.stderr.split("\n"):
    if "(audio)" in line and '"' in line:
        # Extract device name
        import re
        match = re.search(r'"([^"]+)"\s*\(audio\)', line)
        if match:
            print(f"  - {match.group(1)}")

print("\n" + "=" * 60)
print("\nTo stream system audio, you need one of these options:\n")
print("Option 1: Enable 'Stereo Mix' (built into Windows)")
print("  1. Right-click speaker icon → Sounds")
print("  2. Recording tab → Right-click → Show Disabled Devices")
print("  3. Enable 'Stereo Mix' → Set as Default")
print()
print("Option 2: Install VB-Audio Virtual Cable (RECOMMENDED)")
print("  1. Download: https://vb-audio.com/Cable/")
print("  2. Install VB-CABLE Driver")
print("  3. Set VB-Cable as default playback device")
print("  4. It will appear in the list above as 'CABLE Output'")
print()
print("=" * 60)
