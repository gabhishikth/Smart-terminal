"""
check_voice_deps.py
Run this with the EXACT SAME command you use to run smart_terminal.py
e.g. if you normally do `python smart_terminal.py`, run `python check_voice_deps.py`
If you normally do `python3 smart_terminal.py`, run `python3 check_voice_deps.py`
"""

import sys

print("=" * 60)
print("Python interpreter being used:")
print(sys.executable)
print("Python version:", sys.version)
print("=" * 60)

print("\n[1] Trying to import speech_recognition...")
try:
    import speech_recognition as sr
    print("    ✅ SUCCESS —", sr.__file__)
except ImportError as e:
    print("    ❌ FAILED —", e)

print("\n[2] Trying to import pyaudio...")
try:
    import pyaudio
    print("    ✅ SUCCESS —", pyaudio.__file__)
except ImportError as e:
    print("    ❌ FAILED —", e)

print("\n[3] Trying to actually open the microphone (this is what really matters)...")
try:
    import speech_recognition as sr
    mic = sr.Microphone()
    print("    ✅ SUCCESS — microphone object created fine")
    print("    Available microphones:")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"      {i}: {name}")
except Exception as e:
    print("    ❌ FAILED —", type(e).__name__, "-", e)

print("\n[4] Trying to import pyttsx3 (text-to-speech, optional)...")
try:
    import pyttsx3
    print("    ✅ SUCCESS —", pyttsx3.__file__)
except ImportError as e:
    print("    ❌ FAILED —", e)

print("\n" + "=" * 60)
print("Copy this whole output back if anything shows ❌ FAILED")
print("=" * 60)