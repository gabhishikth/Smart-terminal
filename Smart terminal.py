"""
╔══════════════════════════════════════════════════════╗
║           SMART TERMINAL ASSISTANT                   ║
║     AI-Powered Command Interpreter for Windows       ║
╚══════════════════════════════════════════════════════╝

Commands supported:
  Browser   : open browser, open chrome, open firefox
  URLs      : open youtube.com / go to google.com
  Search    : search python tutorials / google what is AI
  Files     : open file notes.txt / open folder Downloads
  Apps      : open notepad / open calculator / open vlc
  System    : shutdown / restart / lock / sleep
  Volume    : volume up / volume down / mute / unmute
  Clipboard : copy hello world / paste
  Screenshot: screenshot
  Music     : play music / pause music (if VLC installed)
  Date/Time : what time is it / what is today's date
  Weather   : weather / weather in Chennai
  Jokes     : tell me a joke
  Math      : calculate 25 * 48
  Create    : create file test.txt / create folder MyFolder
  Delete    : delete file test.txt
  List      : list files / list folder Downloads
  Run       : run notepad.exe / run any command
  Voice     : voice / voice mode / text mode
  Help      : help / commands
  Exit      : exit / quit / bye
"""

import os
import sys
import time
import math
import random
import shutil
import subprocess
import webbrowser
import datetime
import platform
import ctypes
import re
import difflib

# ── Optional imports ──────────────────────────────────
try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import speech_recognition as sr
    import pyaudio
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()  # reads .env file in the project folder, if present
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    HAS_AI = bool(GEMINI_API_KEY)
    if HAS_AI:
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
except ImportError:
    HAS_AI = False
    GEMINI_API_KEY = None
    _genai_client = None

# ─────────────────────────────────────────────────────
# Terminal Colors (Windows ANSI support)
# ─────────────────────────────────────────────────────
os.system("color")  # Enable ANSI on Windows

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
WHITE  = "\033[97m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ─────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────
def print_banner():
    banner = f"""
{GREEN}╔══════════════════════════════════════════════════════════╗
║  {CYAN}{BOLD}  ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗{GREEN}          ║
║  {CYAN}{BOLD}  ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝{GREEN}          ║
║  {CYAN}{BOLD}  ███████╗██╔████╔██║███████║██████╔╝   ██║   {GREEN}           ║
║  {CYAN}{BOLD}  ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   {GREEN}           ║
║  {CYAN}{BOLD}  ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   {GREEN}           ║
║  {CYAN}{BOLD}  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝  {GREEN}           ║
║                                                          ║
║  {YELLOW}        AI-Powered Terminal Assistant v1.0{GREEN}            ║
║  {DIM}        Type 'help' to see all commands{GREEN}                ║
╚══════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def respond(msg, color=GREEN):
    print(f"{color}  ➤  {msg}{RESET}")

def error(msg):
    print(f"{RED}  ✗  {msg}{RESET}")

def success(msg):
    print(f"{GREEN}  ✓  {msg}{RESET}")

def info(msg):
    print(f"{CYAN}  ℹ  {msg}{RESET}")

def thinking():
    print(f"{DIM}  ...processing{RESET}", end="\r")

def contains(text, *keywords):
    return any(k in text for k in keywords)

def after(text, keyword):
    """Return the substring after a keyword."""
    idx = text.find(keyword)
    if idx == -1:
        return ""
    return text[idx + len(keyword):].strip()

# ─────────────────────────────────────────────────────
# Voice Input / Output
# ─────────────────────────────────────────────────────
_tts_engine = None

def init_tts():
    """Lazily initialize the TTS engine so startup stays fast if unused."""
    global _tts_engine
    if _tts_engine is None and HAS_TTS:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", 175)
        _tts_engine.setProperty("volume", 1.0)
    return _tts_engine

def speak(text):
    """Print + speak a response. Falls back to print-only if TTS unavailable."""
    engine = init_tts()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass  # never let TTS errors kill the assistant

_recognizer = None

def init_recognizer():
    global _recognizer
    if _recognizer is None and HAS_VOICE:
        _recognizer = sr.Recognizer()
        _recognizer.energy_threshold = 300
        _recognizer.pause_threshold = 0.8
        _recognizer.dynamic_energy_threshold = True
    return _recognizer

def listen_command(timeout=5, phrase_time_limit=None):
    """
    Listens on the default microphone and returns recognized text (lowercased),
    or None if nothing was understood / no mic input arrived in time.

    phrase_time_limit=None means no hard cap on how long you can talk —
    it stops when it detects a pause (pause_threshold), not a fixed duration.
    This matters once you're asking longer conversational questions, not just
    short commands like "open chrome".
    """
    if not HAS_VOICE:
        error("Voice mode needs: pip install SpeechRecognition pyaudio")
        return None

    recognizer = init_recognizer()
    try:
        with sr.Microphone() as source:
            print(f"{CYAN}  🎙  Listening...{RESET}")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        print(f"{DIM}  ...recognizing{RESET}", end="\r")
        command = recognizer.recognize_google(audio)  # needs internet
        print(f"{GREEN}  🗣  You said: {BOLD}{command}{RESET}")
        return command.lower()

    except sr.WaitTimeoutError:
        info("No speech detected, listening again...")
        return None
    except sr.UnknownValueError:
        error("Could not understand audio. Try again.")
        return None
    except sr.RequestError as e:
        error(f"Speech service error: {e}")
        return None

# ─────────────────────────────────────────────────────
# AI Conversational Fallback (Gemini)
# ─────────────────────────────────────────────────────
_gemini_chat = None

SYSTEM_CONTEXT = (
    "You are the fallback brain of a Windows command-line assistant called "
    "Smart Terminal. The user's input didn't match any of the assistant's "
    "built-in keyword commands, so it's come to you instead. "
    "You have tools available — use them whenever the user's request maps to "
    "one, instead of just describing what you'd do. For anything that isn't "
    "a tool (general questions, conversation), just answer directly. "
    "Keep replies to 1-4 sentences, conversational, no markdown formatting — "
    "this is a terminal, not a chat app."
)

def init_gemini_chat():
    global _gemini_chat

    if _gemini_chat is not None:
        return _gemini_chat

    if not GEMINI_API_KEY:
        error("GEMINI_API_KEY is missing. Check your .env file.")
        return None

    try:
        _gemini_chat = _genai_client.chats.create(
            model="gemini-3.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_CONTEXT,
                tools=AI_TOOLS,
            )
        )
        return _gemini_chat

    except Exception as e:
        error(f"Gemini initialization failed: {e}")
        return None

def ask_ai(user_text):
    if not HAS_AI:
        error("Gemini AI is not configured. Check GEMINI_API_KEY in .env")
        return None

    try:
        chat = init_gemini_chat()

        if chat is None:
            error("Could not initialize Gemini chat.")
            return None

        reply = chat.send_message(user_text)
        return reply.text.strip()

    except Exception as e:
        error(f"AI request failed: {e}")
        return None

# ─────────────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────────────

def cmd_help():
    voice_status = "installed" if HAS_VOICE else "not installed (pip install SpeechRecognition pyaudio)"
    help_text = f"""
{CYAN}{BOLD}  ╔══════════════════════════════════════════╗
  ║           AVAILABLE COMMANDS              ║
  ╚══════════════════════════════════════════╝{RESET}

{YELLOW}  BROWSER & WEB{RESET}
    open browser / open chrome / open firefox / open edge
    open youtube.com       → opens any website
    search python tutorial → Google search
    google what is numpy   → Google search

{YELLOW}  FILES & FOLDERS{RESET}
    open file notes.txt    → opens a file
    open folder Downloads  → opens a folder
    C:\\Users\\you\\file.txt  → opens any path directly, no keyword needed
    create file test.txt   → creates a file
    create folder MyFolder → creates a folder
    delete file test.txt   → deletes a file
    list files             → lists current directory
    list folder Downloads  → lists a folder

{YELLOW}  APPLICATIONS{RESET}
    open notepad / open calculator / open paint
    open task manager / open settings / open camera
    open vlc / open spotify / open word / open excel

{YELLOW}  SYSTEM{RESET}
    shutdown               → shutdown PC
    restart                → restart PC
    lock                   → lock screen
    sleep                  → sleep PC
    screenshot              → takes a screenshot
    volume up / volume down / mute / unmute
    battery                → battery status

{YELLOW}  DATE & TIME{RESET}
    what time is it        → current time
    what is today's date   → current date
    day                    → current day

{YELLOW}  MATH{RESET}
    calculate 25 * 48 + 10 → evaluates expression
    what is 100 / 4        → same

{YELLOW}  CLIPBOARD{RESET}
    copy Hello World       → copies text to clipboard
    paste                  → shows clipboard content

{YELLOW}  FUN{RESET}
    tell me a joke         → random joke
    flip a coin            → heads or tails
    roll a dice            → 1–6
    random number 1 100    → random in range

{YELLOW}  WEATHER{RESET}
    weather                → weather (needs internet)
    weather in Chennai     → weather for city

{YELLOW}  VOICE{RESET}
    voice / voice mode     → switch to speaking commands ({voice_status})
    text / text mode       → switch back to typing

{YELLOW}  OTHER{RESET}
    run notepad.exe        → run any exe/command
    whoami                 → current user
    ip address             → local IP
    ping google.com        → ping a site
    clear                  → clear screen
    exit / quit / bye      → exit terminal
"""
    print(help_text)

# ── Browser & Web ────────────────────────────────────
# Known browser install locations, checked before falling back to PATH.
# Module-level so both cmd_browser() and the AI tool can share it.
BROWSER_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "opera": [
        os.path.expanduser(r"~\AppData\Local\Programs\Opera\opera.exe"),
    ],
    "brave": [
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ],
}

def resolve_browser_path(name):
    """
    Returns a real, launchable path for a browser name, or None if it
    genuinely can't be found. Checks known install locations first
    (BROWSER_PATHS), then falls back to shutil.which() to check PATH —
    unlike a bare subprocess.Popen(name, shell=True), which.() actually
    tells us honestly whether the executable exists before we claim success.
    """
    low = name.lower().strip()
    if low not in BROWSER_PATHS:
        return None
    for path in BROWSER_PATHS[low]:
        if os.path.exists(path):
            return path
    return shutil.which(low)  # last resort: is it on PATH at all?

def cmd_browser(cmd):
    for name in BROWSER_PATHS:
        if name in cmd:
            path = resolve_browser_path(name)
            if path:
                subprocess.Popen([path] if path.endswith(".exe") else path, shell=not path.endswith(".exe"))
                success(f"Opening {name.title()}...")
            else:
                error(f"{name.title()} not found. Is it installed?")
            return
    webbrowser.open_new_tab("https://www.google.com")
    success("Opening default browser...")

def cmd_open_url(cmd):
    # Extract URL-like patterns
    url_match = re.search(r'([\w\-]+\.(com|org|net|io|edu|gov|in|co|uk|youtube|google|github)[\S]*)', cmd)
    if url_match:
        url = url_match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        success(f"Opening {url}")
        return True
    return False

def cmd_search(cmd):
    query = ""
    for kw in ["search for", "search", "google"]:
        if kw in cmd:
            query = after(cmd, kw)
            break
    if query:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        success(f"Searching Google for: {query}")
    else:
        error("What should I search for?")

# ── Files & Folders ──────────────────────────────────
COMMON_FOLDERS = {
    "downloads":  os.path.expanduser("~/Downloads"),
    "desktop":    os.path.expanduser("~/Desktop"),
    "documents":  os.path.expanduser("~/Documents"),
    "pictures":   os.path.expanduser("~/Pictures"),
    "music":      os.path.expanduser("~/Music"),
    "videos":     os.path.expanduser("~/Videos"),
}

def resolve_path(name):
    low = name.lower().strip()
    if low in COMMON_FOLDERS:
        return COMMON_FOLDERS[low]
    if os.path.exists(name):
        return name
    # try Desktop
    desk = os.path.join(os.path.expanduser("~/Desktop"), name)
    if os.path.exists(desk):
        return desk

    # Not an exact known location — search common folders by name.
    found = search_common_locations(name)
    if found:
        return found

    return name  # nothing matched, return as-is and let the OS report the error


# Folders searched when a bare name is given (no path, no exact match above).
# Order matters — earlier folders are preferred when a name exists in multiple.
SEARCH_ROOTS = [
    COMMON_FOLDERS["desktop"],
    COMMON_FOLDERS["documents"],
    COMMON_FOLDERS["downloads"],
    COMMON_FOLDERS["pictures"],
    COMMON_FOLDERS["music"],
    COMMON_FOLDERS["videos"],
]

# Skip these when walking — they're huge, irrelevant, or slow to traverse.
SEARCH_SKIP_DIRS = {"node_modules", ".git", "venv", "__pycache__", ".cache", "site-packages", "appdata"}

SEARCH_MAX_DEPTH = 3  # how many folder levels deep to search under each root


def search_common_locations(name, max_depth=SEARCH_MAX_DEPTH):
    """
    Searches Desktop/Documents/Downloads/Pictures/Music/Videos (a few levels
    deep) for a file or folder matching `name`. Tries an exact filename match
    first; if nothing exact is found, falls back to a fuzzy match so small
    typos ("report.doc" vs "report.docx") still resolve.

    This deliberately does NOT search the whole C: drive — that's slow
    (can take a minute+) and would make every 'open' command feel laggy.
    A dedicated full-drive search is a better fit as its own command later.
    """
    target_low = name.lower()
    all_names = {}  # lowercase entry name -> full path (first one seen wins)

    for root in SEARCH_ROOTS:
        if not os.path.isdir(root):
            continue
        root_depth = root.rstrip(os.sep).count(os.sep)

        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath.rstrip(os.sep).count(os.sep) - root_depth
            if depth >= max_depth:
                dirnames[:] = []  # don't descend further
            dirnames[:] = [d for d in dirnames if d.lower() not in SEARCH_SKIP_DIRS]

            for entry in dirnames + filenames:
                entry_low = entry.lower()
                full_path = os.path.join(dirpath, entry)

                if entry_low == target_low:
                    return full_path  # exact match — stop immediately

                all_names.setdefault(entry_low, full_path)

    # No exact match anywhere — try a fuzzy match across everything we saw.
    close = difflib.get_close_matches(target_low, all_names.keys(), n=1, cutoff=0.6)
    if close:
        matched_path = all_names[close[0]]
        info(f"No exact match for '{name}' — using closest match: {os.path.basename(matched_path)}")
        return matched_path

    return None

def cmd_open_path(cmd):
    """
    Opens a raw Windows path like 'C:\\Users\\you\\Desktop\\notes.txt' or
    'D:\\Projects' directly — works whether it's a file or a folder, and
    doesn't require the words 'file' or 'folder' in the command.
    """
    match = re.search(r'[a-zA-Z]:[\\/][^\s"]*(?:\s[^\s"]+)*', cmd)
    if not match:
        return False

    raw = match.group(0).strip().rstrip(".,;")

    # The regex can over-capture trailing words ("...report.docx please").
    # Try the full match first, then trim one word at a time from the end
    # until something on disk actually matches.
    words = raw.split(" ")
    path = None
    for end in range(len(words), 0, -1):
        candidate = " ".join(words[:end]).rstrip(".,;")
        if os.path.exists(candidate):
            path = candidate
            break

    if path is None:
        # Nothing on disk matched at any length — report the shortest,
        # most literal interpretation (first word only) as the failure.
        path = words[0]
        error(f"Path not found: {path}")
        return True  # matched a drive path, just didn't exist — don't fall through to Apps

    try:
        os.startfile(path)
        if os.path.isdir(path):
            success(f"Opening folder: {path}")
        else:
            success(f"Opening: {path}")
    except Exception as e:
        error(f"Could not open: {e}")
    return True

def cmd_open_file(cmd):
    path = after(cmd, "open file").strip() or after(cmd, "open").strip()
    path = resolve_path(path)
    try:
        os.startfile(path)
        success(f"Opening: {path}")
    except Exception as e:
        error(f"Could not open file: {e}")

def cmd_open_folder(cmd):
    for kw in ["open folder", "open directory", "open dir"]:
        if kw in cmd:
            folder = after(cmd, kw).strip()
            break
    else:
        folder = ""
    folder = resolve_path(folder) if folder else os.getcwd()
    try:
        os.startfile(folder)
        success(f"Opening folder: {folder}")
    except Exception as e:
        error(f"Could not open folder: {e}")

def cmd_open_bare(cmd):
    """
    Last-resort handler for 'open <name>' where <name> wasn't a recognized
    app, URL, or full path. Searches common folders (via resolve_path's
    search fallback) so things like 'open report.docx' or 'open my resume'
    just work without needing the exact location.
    """
    name = ""
    for kw in ["open ", "launch ", "start "]:
        if cmd.startswith(kw):
            name = cmd[len(kw):].strip()
            break
    if not name:
        return False

    resolved = resolve_path(name)
    if resolved == name or not os.path.exists(resolved):
        return False  # nothing found — let it fall through to AI/unknown

    try:
        os.startfile(resolved)
        if os.path.isdir(resolved):
            success(f"Opening folder: {resolved}")
        else:
            success(f"Opening: {resolved}")
    except Exception as e:
        error(f"Could not open: {e}")
    return True

def cmd_create_file(cmd):
    name = after(cmd, "create file").strip()
    if not name:
        error("Please specify a file name. E.g.: create file notes.txt")
        return
    try:
        with open(name, "w") as f:
            f.write("")
        success(f"Created file: {name}")
    except Exception as e:
        error(f"Could not create file: {e}")

def cmd_create_folder(cmd):
    name = after(cmd, "create folder").strip() or after(cmd, "create directory").strip()
    if not name:
        error("Please specify a folder name.")
        return
    try:
        os.makedirs(name, exist_ok=True)
        success(f"Created folder: {name}")
    except Exception as e:
        error(f"Could not create folder: {e}")

def cmd_delete_file(cmd):
    name = after(cmd, "delete file").strip()
    if not name:
        error("Specify file to delete. E.g.: delete file test.txt")
        return
    confirm = input(f"{YELLOW}  ⚠  Delete '{name}'? (yes/no): {RESET}").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            os.remove(name)
            success(f"Deleted: {name}")
        except Exception as e:
            error(f"Could not delete: {e}")
    else:
        info("Cancelled.")

def cmd_list_files(cmd):
    folder = ""
    if "list folder" in cmd:
        folder = after(cmd, "list folder").strip()
    elif "list directory" in cmd:
        folder = after(cmd, "list directory").strip()
    folder = resolve_path(folder) if folder else os.getcwd()
    try:
        items = os.listdir(folder)
        print(f"\n{CYAN}  📁 Contents of: {folder}{RESET}")
        for item in sorted(items):
            full = os.path.join(folder, item)
            icon = "📁" if os.path.isdir(full) else "📄"
            print(f"     {icon} {item}")
        print()
    except Exception as e:
        error(f"Could not list: {e}")

# ── Applications ─────────────────────────────────────
APPS = {
    "notepad":        "notepad.exe",
    "calculator":     "calc.exe",
    "paint":          "mspaint.exe",
    "word pad":       "write.exe",
    "wordpad":        "write.exe",
    "task manager":   "taskmgr.exe",
    "settings":       "ms-settings:",
    "camera":         "microsoft.windows.camera:",
    "store":          "ms-windows-store:",
    "calendar":       "outlookcal:",
    "maps":           "bingmaps:",
    "mail":           "mailto:",
    "cmd":            "cmd.exe",
    "powershell":     "powershell.exe",
    "snipping tool":  "snippingtool.exe",
    "magnifier":      "magnify.exe",
    "on screen keyboard": "osk.exe",
    "character map":  "charmap.exe",
    "disk cleanup":   "cleanmgr.exe",
    "regedit":        "regedit.exe",
    "vlc":            "vlc",
    "spotify":        "spotify",
    "excel":          "excel",
    "word":           "winword",
    "powerpoint":     "powerpnt",
    "outlook":        "outlook",
    "vs code":        "code",
    "vscode":         "code",
    "visual studio code": "code",
    "sublime":        "sublime_text",
    "chrome":         "chrome",
    "firefox":        "firefox",
    "edge":           "msedge",
}

def cmd_open_app(cmd):
    for app_name, exe in APPS.items():
        if app_name in cmd:
            try:
                if exe.endswith(":"):
                    os.startfile(exe)
                else:
                    subprocess.Popen(exe, shell=True)
                success(f"Opening {app_name.title()}...")
                return True
            except Exception as e:
                error(f"Could not open {app_name}: {e}")
                return True
    return False

# ── System Commands ──────────────────────────────────
def cmd_shutdown(cmd):
    confirm = input(f"{RED}  ⚠  Shutdown the computer? (yes/no): {RESET}").strip().lower()
    if confirm in ["yes", "y"]:
        success("Shutting down...")
        time.sleep(1)
        os.system("shutdown /s /t 5")
    else:
        info("Shutdown cancelled.")

def cmd_restart(cmd):
    confirm = input(f"{YELLOW}  ⚠  Restart the computer? (yes/no): {RESET}").strip().lower()
    if confirm in ["yes", "y"]:
        success("Restarting...")
        time.sleep(1)
        os.system("shutdown /r /t 5")
    else:
        info("Restart cancelled.")

def cmd_lock():
    success("Locking screen...")
    ctypes.windll.user32.LockWorkStation()

def cmd_sleep():
    success("Going to sleep...")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def cmd_screenshot():
    try:
        import PIL.ImageGrab as ImageGrab
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~/Desktop"), f"screenshot_{ts}.png")
        img = ImageGrab.grab()
        img.save(path)
        success(f"Screenshot saved to Desktop: screenshot_{ts}.png")
    except ImportError:
        # fallback using snipping tool
        subprocess.Popen("snippingtool.exe")
        info("Opened Snipping Tool (install Pillow for auto-screenshot: pip install pillow)")

def cmd_volume(cmd):
    # Pure PowerShell via SendKeys - no packages needed
    try:
        wsh = "(New-Object -ComObject WScript.Shell)"
        if "unmute" in cmd or "mute" in cmd:
            ps = wsh + ".SendKeys([char]173)"
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
            success("Mute toggled.")
        elif "volume up" in cmd:
            ps = "$w=" + wsh + "; 1..5 | ForEach-Object { $w.SendKeys([char]175) }"
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
            success("Volume increased.")
        elif "volume down" in cmd:
            ps = "$w=" + wsh + "; 1..5 | ForEach-Object { $w.SendKeys([char]174) }"
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
            success("Volume decreased.")
    except Exception as e:
        error(f"Volume control failed: {e}")

# ── Date & Time ──────────────────────────────────────
def cmd_time():
    now = datetime.datetime.now()
    respond(f"Current time: {BOLD}{now.strftime('%I:%M:%S %p')}{RESET}")

def cmd_date():
    now = datetime.datetime.now()
    respond(f"Today is: {BOLD}{now.strftime('%A, %d %B %Y')}{RESET}")

# ── Math ─────────────────────────────────────────────
def cmd_calculate(cmd):
    expr = ""
    for kw in ["calculate", "what is", "compute", "eval"]:
        if kw in cmd:
            expr = after(cmd, kw).strip()
            break
    if not expr:
        error("What should I calculate?")
        return
    # safe eval
    try:
        allowed = set("0123456789+-*/.() %")
        clean = "".join(c for c in expr if c in allowed or c == "^")
        clean = clean.replace("^", "**")
        result = eval(clean, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
        respond(f"{expr} = {BOLD}{result}{RESET}")
    except Exception:
        error(f"Could not calculate: {expr}")

# ── Clipboard ────────────────────────────────────────
def cmd_copy(cmd):
    text = after(cmd, "copy").strip()
    if not text:
        error("What should I copy?")
        return
    if HAS_CLIPBOARD:
        pyperclip.copy(text)
        success(f"Copied to clipboard: {text}")
    else:
        error("Install pyperclip: pip install pyperclip")

def cmd_paste():
    if HAS_CLIPBOARD:
        text = pyperclip.paste()
        respond(f"Clipboard: {BOLD}{text}{RESET}")
    else:
        error("Install pyperclip: pip install pyperclip")

# ── Weather ──────────────────────────────────────────
def cmd_weather(cmd):
    city = ""
    if "weather in" in cmd:
        city = after(cmd, "weather in").strip()
    elif "weather for" in cmd:
        city = after(cmd, "weather for").strip()

    if not HAS_REQUESTS:
        error("Install requests: pip install requests")
        return
    try:
        url = f"https://wttr.in/{city}?format=3"
        r = requests.get(url, timeout=5)
        respond(r.text.strip())
    except Exception:
        error("Could not fetch weather. Check internet connection.")

# ── System Info ──────────────────────────────────────
def cmd_whoami():
    respond(f"User: {BOLD}{os.getlogin()}{RESET}")

def cmd_ip():
    import socket
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    respond(f"Hostname: {BOLD}{hostname}{RESET}")
    respond(f"IP Address: {BOLD}{ip}{RESET}")

def cmd_battery():
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            status = "Charging" if battery.power_plugged else "Discharging"
            respond(f"Battery: {BOLD}{battery.percent:.0f}%{RESET} ({status})")
        else:
            info("No battery found (desktop PC?)")
    except ImportError:
        error("Install psutil: pip install psutil")

def cmd_ping(cmd):
    host = after(cmd, "ping").strip() or "google.com"
    info(f"Pinging {host}...")
    os.system(f"ping -n 4 {host}")

# ── Fun ──────────────────────────────────────────────
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "Why did the computer go to the doctor? It had a virus! 🦠",
    "Why do Java developers wear glasses? Because they don't C#! 👓",
    "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?' 🍺",
    "Why did the programmer quit his job? Because he didn't get arrays! 💰",
    "What's a computer's favourite snack? Microchips! 🍟",
    "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings! 😢",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem! 💡",
]

def cmd_joke():
    respond(random.choice(JOKES), color=YELLOW)

def cmd_coin():
    result = random.choice(["HEADS 🪙", "TAILS 🪙"])
    respond(f"Flipping a coin... {BOLD}{result}{RESET}")

def cmd_dice():
    result = random.randint(1, 6)
    respond(f"Rolling a dice... {BOLD}{result} 🎲{RESET}")

def cmd_random_number(cmd):
    nums = re.findall(r'\d+', cmd)
    if len(nums) >= 2:
        lo, hi = int(nums[0]), int(nums[1])
    else:
        lo, hi = 1, 100
    respond(f"Random number ({lo}–{hi}): {BOLD}{random.randint(lo, hi)}{RESET}")

# ── Run arbitrary command ────────────────────────────
def cmd_run(cmd):
    raw = after(cmd, "run").strip()
    if not raw:
        error("What should I run?")
        return
    try:
        subprocess.Popen(raw, shell=True)
        success(f"Running: {raw}")
    except Exception as e:
        error(f"Failed: {e}")

# ─────────────────────────────────────────────────────
# AI Tool Functions
# ─────────────────────────────────────────────────────
# These are exposed to Gemini as "tools" it can choose to call when the
# router doesn't match anything (see ask_ai() / init_gemini_chat()).
#
# Each one takes clean, typed arguments (not a raw command string) and
# RETURNS a plain-text description of what happened — that return value
# is what Gemini reads to write its final reply. The Google GenAI SDK
# generates the tool's schema straight from the type hints + docstring
# below, so both need to be accurate and descriptive.
#
# Deliberately NOT exposed as tools: shutdown, restart, delete file, run
# (arbitrary command execution). Those stay keyword-only in route(), with
# their existing yes/no confirmation — an LLM should never have a direct
# path to destructive system actions.

def tool_open_application(app_name: str) -> str:
    """Opens a Windows application by name, such as Notepad, Chrome, Calculator, VS Code, or Spotify.
    For opening a specific website, use tool_open_website instead — this tool only
    launches the application itself, with no destination page.

    Args:
        app_name: The name of the application to open, e.g. 'notepad', 'chrome', 'calculator'.
    """
    low = app_name.lower().strip()
    for name, exe in APPS.items():
        if name in low or low in name:
            # Browsers get special handling — they're often not on PATH by
            # default, so we check known install locations first (same
            # logic cmd_browser uses) instead of blindly trusting Popen.
            if name in BROWSER_PATHS:
                path = resolve_browser_path(name)
                if not path:
                    error(f"{name.title()} not found. Is it installed?")
                    return f"Couldn't find {name} — it doesn't appear to be installed."
                subprocess.Popen([path] if path.endswith(".exe") else path, shell=not path.endswith(".exe"))
                success(f"Opening {name.title()}...")
                return f"Opened {name}."

            # Non-browser apps: verify the executable actually resolves
            # before claiming success, so a missing app can't silently
            # report as opened.
            if exe.endswith(":"):
                try:
                    os.startfile(exe)
                    success(f"Opening {name.title()}...")
                    return f"Opened {name}."
                except Exception as e:
                    error(f"Could not open {name}: {e}")
                    return f"Failed to open {name}: {e}"

            if shutil.which(exe) is None:
                error(f"{name.title()} not found. Is it installed?")
                return f"Couldn't find {name} — it doesn't appear to be installed or isn't on PATH."

            subprocess.Popen(exe, shell=True)
            success(f"Opening {name.title()}...")
            return f"Opened {name}."

    return f"'{app_name}' isn't a recognized application."

def tool_open_website(site: str) -> str:
    """Opens a website in the default browser. Accepts a full URL, a bare
    domain, or just a common site name — builds the correct URL either way.
    Use this whenever the user wants to visit or open a specific website
    (e.g. YouTube, GitHub) rather than just launching a browser with no destination.

    Args:
        site: A website name or URL, e.g. 'youtube', 'youtube.com', or 'https://youtube.com'.
    """
    low = site.lower().strip()
    if not re.search(r'\.\w{2,}', low):
        low = low + ".com"  # bare name like 'youtube' -> 'youtube.com'
    if not low.startswith("http"):
        low = "https://" + low
    try:
        webbrowser.open(low)
        success(f"Opening {low}")
        return f"Opened {low} in the default browser."
    except Exception as e:
        error(f"Could not open {low}: {e}")
        return f"Failed to open {low}: {e}"

def tool_open_file_or_folder(name: str) -> str:
    """Opens a file or folder on the user's computer, given its name or a full path.
    Searches Desktop, Documents, Downloads, Pictures, Music, and Videos if only a
    name is given (not a full path).

    Args:
        name: A file/folder name (e.g. 'report.docx') or a full Windows path
            (e.g. 'C:\\Users\\you\\Desktop\\notes.txt').
    """
    resolved = resolve_path(name)
    if resolved == name and not os.path.exists(resolved):
        return f"Couldn't find a file or folder named '{name}'."
    try:
        os.startfile(resolved)
        kind = "folder" if os.path.isdir(resolved) else "file"
        success(f"Opening {kind}: {resolved}")
        return f"Opened the {kind}: {resolved}"
    except Exception as e:
        error(f"Could not open: {e}")
        return f"Found '{name}' but couldn't open it: {e}"

def tool_get_weather(city: str = "") -> str:
    """Gets the current weather for a city. If no city is given, uses the
    server's default location based on IP.

    Args:
        city: City name, e.g. 'Chennai'. Leave empty for local weather.
    """
    if not HAS_REQUESTS:
        return "Weather isn't available — the requests library isn't installed."
    try:
        url = f"https://wttr.in/{city}?format=3"
        r = requests.get(url, timeout=5)
        text = r.text.strip()
        respond(text)
        return text
    except Exception:
        return "Couldn't fetch weather — check the internet connection."

def tool_calculate(expression: str) -> str:
    """Evaluates a math expression and returns the numeric result.

    Args:
        expression: A math expression using +, -, *, /, ^, parentheses, e.g. '25 * 48 + 10'.
    """
    try:
        allowed = set("0123456789+-*/.() %")
        clean = "".join(c for c in expression if c in allowed or c == "^")
        clean = clean.replace("^", "**")
        result = eval(clean, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
        respond(f"{expression} = {BOLD}{result}{RESET}")
        return f"{expression} = {result}"
    except Exception:
        return f"Couldn't evaluate '{expression}' — it doesn't look like a valid expression."

def tool_tell_joke() -> str:
    """Tells a random short programming joke."""
    joke = random.choice(JOKES)
    respond(joke, color=YELLOW)
    return joke

def tool_get_current_time() -> str:
    """Returns the current time."""
    now = datetime.datetime.now()
    text = now.strftime("%I:%M:%S %p")
    respond(f"Current time: {BOLD}{text}{RESET}")
    return f"The current time is {text}."

def tool_get_current_date() -> str:
    """Returns today's date."""
    now = datetime.datetime.now()
    text = now.strftime("%A, %d %B %Y")
    respond(f"Today is: {BOLD}{text}{RESET}")
    return f"Today's date is {text}."

def tool_get_battery_status() -> str:
    """Returns the laptop's current battery percentage and charging status."""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            status = "charging" if battery.power_plugged else "discharging"
            text = f"{battery.percent:.0f}% ({status})"
            respond(f"Battery: {BOLD}{text}{RESET}")
            return f"Battery is at {text}."
        return "No battery detected — this might be a desktop PC."
    except ImportError:
        return "Battery status isn't available — the psutil library isn't installed."

# Tools Gemini is allowed to call. The SDK auto-executes whichever one the
# model chooses, then feeds the return value back in to write its reply.
AI_TOOLS = [
    tool_open_application,
    tool_open_website,
    tool_open_file_or_folder,
    tool_get_weather,
    tool_calculate,
    tool_tell_joke,
    tool_get_current_time,
    tool_get_current_date,
    tool_get_battery_status,
]

# ─────────────────────────────────────────────────────
# Main Router
# ─────────────────────────────────────────────────────
def route(cmd):
    cmd = cmd.strip()
    low = cmd.lower()

    # ── Exit ───────────────────────────────────────
    if low in ["exit", "quit", "bye", "q"]:
        print(f"\n{CYAN}  Goodbye! Have a great day! 👋{RESET}\n")
        sys.exit(0)

    # ── Clear ──────────────────────────────────────
    if low in ["clear", "cls"]:
        os.system("cls")
        print_banner()
        return

    # ── Help ───────────────────────────────────────
    if contains(low, "help", "commands", "what can you do"):
        cmd_help()
        return

    # ── Date / Time ────────────────────────────────
    if contains(low, "what time", "current time", "time now"):
        cmd_time(); return
    if contains(low, "what day", "today's date", "what date", "current date"):
        cmd_date(); return
    if low in ["time"]:
        cmd_time(); return
    if low in ["date", "day"]:
        cmd_date(); return

    # ── Math ───────────────────────────────────────
    if contains(low, "calculate", "compute") or \
       (contains(low, "what is") and any(op in low for op in ["+","-","*","/","^","%"])):
        cmd_calculate(low); return

    # ── System ─────────────────────────────────────
    if contains(low, "shutdown", "shut down"):
        cmd_shutdown(low); return
    if contains(low, "restart", "reboot"):
        cmd_restart(low); return
    if contains(low, "lock screen", "lock pc", "lock computer"):
        cmd_lock(); return
    if contains(low, "sleep", "hibernate"):
        cmd_sleep(); return
    if contains(low, "screenshot", "screen shot", "capture screen"):
        cmd_screenshot(); return
    if contains(low, "volume up", "increase volume"):
        cmd_volume(low); return
    if contains(low, "volume down", "decrease volume", "lower volume"):
        cmd_volume(low); return
    if contains(low, "unmute"):
        cmd_volume(low); return
    if contains(low, "mute"):
        cmd_volume(low); return
    if contains(low, "battery", "charge"):
        cmd_battery(); return
    if low.startswith("ping"):
        cmd_ping(low); return
    if contains(low, "whoami", "who am i", "current user", "my name"):
        cmd_whoami(); return
    if contains(low, "ip address", "my ip", "ipconfig"):
        cmd_ip(); return

    # ── Weather ────────────────────────────────────
    if contains(low, "weather"):
        cmd_weather(low); return

    # ── Search ─────────────────────────────────────
    if contains(low, "search", "google") and not contains(low, "open"):
        cmd_search(low); return

    # ── Browser ────────────────────────────────────
    if contains(low, "open browser", "open chrome", "open firefox",
                "open edge", "open opera", "open brave"):
        cmd_browser(low); return

    # ── Windows drive path (C:\..., D:\...) ─────────
    if re.search(r'[a-zA-Z]:[\\/]', low):
        if cmd_open_path(low):
            return

    # ── URL open ───────────────────────────────────
    if contains(low, "open", "go to", "visit", "launch") and \
       re.search(r'[\w\-]+\.(com|org|net|io|edu|gov|in|co|youtube|google|github)', low):
        if cmd_open_url(low):
            return

    # ── Files / Folders (explicit keywords) ─────────
    # Checked before Apps so a real file/folder always wins over an
    # incidental app-name collision (e.g. a 'Camera Roll' folder vs
    # the Camera app both containing the word 'camera').
    if contains(low, "open file"):
        cmd_open_file(low); return
    if contains(low, "open folder", "open directory", "open dir"):
        cmd_open_folder(low); return
    if contains(low, "create file", "make file", "new file"):
        cmd_create_file(low); return
    if contains(low, "create folder", "make folder", "new folder", "mkdir"):
        cmd_create_folder(low); return
    if contains(low, "delete file", "remove file"):
        cmd_delete_file(low); return
    if contains(low, "list files", "list folder", "list directory", "show files", "ls", "dir"):
        cmd_list_files(low); return

    # ── Bare "open <name>" — search common folders ──
    # Also checked before Apps, for the same reason as above.
    if contains(low, "open", "launch", "start"):
        if cmd_open_bare(low):
            return

    # ── Apps ───────────────────────────────────────
    # Last resort for "open X" — only reached if X wasn't a real file
    # or folder anywhere in the common search locations.
    if contains(low, "open", "launch", "start"):
        if cmd_open_app(low):
            return

    # ── Clipboard ──────────────────────────────────
    if low.startswith("copy "):
        cmd_copy(low); return
    if low in ["paste", "show clipboard", "clipboard"]:
        cmd_paste(); return

    # ── Fun ────────────────────────────────────────
    if contains(low, "joke", "funny", "make me laugh"):
        cmd_joke(); return
    if contains(low, "flip", "coin", "heads", "tails"):
        cmd_coin(); return
    if contains(low, "roll", "dice"):
        cmd_dice(); return
    if contains(low, "random number", "random num"):
        cmd_random_number(low); return

    # ── Run raw command ────────────────────────────
    if low.startswith("run "):
        cmd_run(low); return

    # ── Unknown → hand off to AI, if configured ─────
    ai_reply = ask_ai(cmd)
    if ai_reply:
        respond(ai_reply, color=CYAN)
        speak(ai_reply)
        return

    respond(f"I don't understand: '{cmd}'. Type {BOLD}help{RESET}{GREEN} to see what I can do.", color=YELLOW)

# ─────────────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────────────
def main():
    os.system("cls")
    print_banner()
    info(f"Running on {platform.system()} {platform.release()} | Python {platform.python_version()}")
    if not HAS_VOICE:
        info("Voice mode disabled — install with: pip install SpeechRecognition pyaudio")
    if HAS_AI:
        info("AI fallback active — Gemini can chat, and call real tools (apps, files, weather, math).")
    else:
        info("AI fallback disabled — set GEMINI_API_KEY in a .env file to enable.")
    print()

    voice_mode = False

    while True:
        try:
            if voice_mode:
                user_input = listen_command()
                if user_input is None:
                    continue  # nothing understood, listen again
                print()
            else:
                user_input = input(f"{GREEN}smart@terminal{RESET}:{CYAN}~{RESET}$ ").strip()
                if not user_input:
                    continue
                print()

            low = user_input.lower()

            # ── Voice mode toggle ───────────────────
            if low in ["voice", "voice mode", "enable voice", "start voice"]:
                if not HAS_VOICE:
                    error("Voice mode needs: pip install SpeechRecognition pyaudio")
                else:
                    voice_mode = True
                    success("Voice mode ON. Speak your commands.")
                    speak("Voice mode activated")
                print()
                continue

            if low in ["text", "text mode", "disable voice", "stop voice"]:
                voice_mode = False
                success("Text mode ON. Type your commands.")
                print()
                continue

            route(user_input)
            print()

        except KeyboardInterrupt:
            if voice_mode:
                voice_mode = False
                print(f"\n{YELLOW}  Voice mode interrupted — switched back to text mode.{RESET}")
                print(f"{CYAN}  Use 'exit' to quit.{RESET}\n")
            else:
                print(f"\n{CYAN}  Use 'exit' to quit.{RESET}\n")
        except SystemExit:
            raise
        except Exception as e:
            error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()