import io
import subprocess
from PIL import Image
import time
import tempfile
import os

def adb_tap(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

def get_device_id():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]  # Skip header
    devices = [line.split()[0] for line in lines if '\tdevice' in line]
    return devices[0] if devices else None

def capture_screen():
    device_id = get_device_id()
    if not device_id:
        raise Exception("No ADB device found")
    
    result = subprocess.run(
        ["adb", "-s", device_id, "exec-out", "screencap", "-p"],
        capture_output=True
    )
    
    # Skip any warning text and find the PNG data
    png_start = result.stdout.find(b'\x89PNG')
    if png_start == -1:
        raise Exception("No PNG data found in screencap output")
    
    return Image.open(io.BytesIO(result.stdout[png_start:]))


def has_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    print("ADB Devices:")
    print(result.stdout)
    
    if "device" not in result.stdout or result.stdout.count('\n') <= 1:
        print("❌ No device connected or not authorized!")
        return False
    return True

if __name__ == "__main__":
    while(not has_devices()):
        time.sleep(5)
    capture_screen().save("art/lvl10.png")