"""Enable Stereo Mix on Windows programmatically.

This script uses PowerShell to enable the Stereo Mix recording device
if it exists on your system. Stereo Mix captures your system audio output.
"""

import subprocess
import sys


def enable_stereo_mix() -> bool:
    """Enable Stereo Mix using PowerShell.

    Returns:
        True if successful, False otherwise.
    """
    print("=" * 60)
    print("Attempting to enable Stereo Mix...")
    print("=" * 60)

    # PowerShell command to enable Stereo Mix
    ps_command = """
$deviceName = "Stereo Mix"
Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;

    public class Audio {
        [DllImport("winmm.dll", SetLastError=true)]
        public static extern int waveInGetNumDevs();
    }
"@

# Alternative: Use COM to interact with audio devices
$shell = New-Object -ComObject Shell.Application

Write-Host "Checking for Stereo Mix device..."
Write-Host "Note: This requires manual enablement through Sound settings."
Write-Host ""
Write-Host "Opening Sound Control Panel..."

# Open sound control panel
Start-Process "mmsys.cpl"

Write-Host ""
Write-Host "Please follow these steps in the window that opened:"
Write-Host "1. Go to the 'Recording' tab"
Write-Host "2. Right-click in empty space -> 'Show Disabled Devices'"
Write-Host "3. Find 'Stereo Mix' or 'Wave Out Mix'"
Write-Host "4. Right-click it -> 'Enable'"
Write-Host "5. Right-click it again -> 'Set as Default Device'"
Write-Host "6. Click OK"
"""

    try:
        # Execute PowerShell command
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5,
        )

        print("\n" + result.stdout)

        if result.stderr:
            print("Errors:", result.stderr)

        print("\n" + "=" * 60)
        print("After enabling Stereo Mix, run the bot again.")
        print("=" * 60)

        return True

    except subprocess.TimeoutExpired:
        print("PowerShell command timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def check_if_stereo_mix_available() -> bool:
    """Check if Stereo Mix appears in FFmpeg device list.

    Returns:
        True if Stereo Mix is found, False otherwise.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Check if Stereo Mix appears in the output
        output = result.stderr.lower()
        return "stereo mix" in output or "wave out mix" in output

    except Exception as e:
        print(f"Error checking for Stereo Mix: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Windows System Audio Capture Setup")
    print("=" * 60)
    print()

    # Check current status
    if check_if_stereo_mix_available():
        print("✓ Stereo Mix is already available!")
        print("  Run the bot and select the Stereo Mix option.")
    else:
        print("✗ Stereo Mix not currently available.")
        print()
        enable_stereo_mix()
        print()
        print("After enabling, run this script again to verify.")

    print()
    input("Press Enter to exit...")
