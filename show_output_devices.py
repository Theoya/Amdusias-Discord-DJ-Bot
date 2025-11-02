"""Show available output devices for routing apps."""

from src.audio_device import AudioDeviceEnumerator

print("=" * 70)
print("Available Audio Output Devices for App Routing")
print("=" * 70)
print()
print("Pick one of these devices to route your apps to:")
print("(The bot will capture from its loopback)")
print()

devices = AudioDeviceEnumerator.enumerate_devices()

# Show only output devices
output_devices = [d for d in devices if d.device_type == "output"]

for device in output_devices:
    print(f"{device.index}. {device.name}")

print()
print("=" * 70)
print("How to route apps to a specific output:")
print("=" * 70)
print()
print("Option 1 - Windows Settings (Per-App):")
print("  1. Right-click speaker icon → 'Open Sound settings'")
print("  2. Scroll down → 'Advanced sound options'")
print("  3. Click 'App volume and device preferences'")
print("  4. For each app (Spotify, Chrome, etc.):")
print("     - Set Output device to one of the devices above")
print()
print("Option 2 - Windows Sound Control Panel:")
print("  1. Right-click speaker icon → 'Sounds'")
print("  2. Playback tab → Select a device → 'Set Default'")
print("  3. All apps will use that device")
print()
print("Recommendation:")
print("  - Use one of the NVIDIA monitor outputs if you don't listen through them")
print("  - Or use 'Line (2- DDJ-FLX2)' if you're not using that")
print("  - Set Discord to output to your real speakers (Realtek)")
print("  - Bot captures from the device you route apps to")
print()
print("=" * 70)
