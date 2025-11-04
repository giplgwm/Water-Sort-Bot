#!/usr/bin/env python3
"""
Water Sort Bot - Main Entry Point
A bot that plays Water Sort puzzle games on Android via ADB
"""
import sys
from adb import has_devices

def main():
    print("=" * 50)
    print("Water Sort Bot")
    print("=" * 50)
    print("\nThis bot automates playing Water Sort puzzle games on Android.")
    print("\nRequirements:")
    print("  1. Android device connected via ADB")
    print("  2. Water Sort game running on the device")
    print("  3. USB debugging enabled on the device")
    print("\nChecking for connected devices...\n")
    
    if has_devices():
        print("\n✓ Device connected and ready!")
        print("\nTo start the bot, run: python game-logic.py")
        print("\nNote: Make sure the Water Sort game is open on your device")
    else:
        print("\n❌ No device found!")
        print("\nTo connect a device:")
        print("  1. Enable USB debugging on your Android device")
        print("  2. Connect via USB cable")
        print("  3. Run 'adb devices' to authorize the connection")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
