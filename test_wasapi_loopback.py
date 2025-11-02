"""Test WASAPI loopback device enumeration."""

import pyaudiowpatch as pyaudio

print("=" * 60)
print("WASAPI Loopback Device Test")
print("=" * 60)

# Initialize PyAudio
p = pyaudio.PyAudio()

print(f"\nFound {p.get_device_count()} audio devices\n")

# List all devices
print("All Audio Devices:")
print("-" * 60)
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"\nDevice {i}: {info['name']}")
    print(f"  Max Input Channels: {info['maxInputChannels']}")
    print(f"  Max Output Channels: {info['maxOutputChannels']}")
    print(f"  Default Sample Rate: {info['defaultSampleRate']}")

    # Check if this is a loopback device
    is_loopback = info.get('isLoopbackDevice', False)
    if is_loopback:
        print(f"  >>> LOOPBACK DEVICE (System Audio Capture) <<<")

# Get default WASAPI loopback device
print("\n" + "=" * 60)
print("Default Loopback Device (System Audio Output):")
print("=" * 60)

try:
    # Get default WASAPI loopback device
    wasapi_info = p.get_default_wasapi_loopback()
    print(f"\nDevice Name: {wasapi_info['name']}")
    print(f"Index: {wasapi_info['index']}")
    print(f"Sample Rate: {wasapi_info['defaultSampleRate']}")
    print(f"Channels: {wasapi_info['maxInputChannels']}")
    print("\n>>> This device will capture your system audio! <<<")
except Exception as e:
    print(f"\nError getting default loopback device: {e}")

p.terminate()

print("\n" + "=" * 60)
print("If you see a loopback device above, the bot can capture")
print("your system audio without needing Stereo Mix or VB-Cable!")
print("=" * 60)
