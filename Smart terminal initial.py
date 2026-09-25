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
# Command Handlers
# ─────────────────────────────────────────────────────

def cmd_help():
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
    screenshot             → takes a screenshot
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
def cmd_browser(cmd):
    import os
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
    for name, paths in BROWSER_PATHS.items():
        if name in cmd:
            for path in paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    success(f"Opening {name.title()}...")
                    return
            try:
                subprocess.Popen(name, shell=True)
                success(f"Opening {name.title()}...")
                return
            except Exception:
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
    return name  # return as-is, let OS handle

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

    # ── URL open ───────────────────────────────────
    if contains(low, "open", "go to", "visit", "launch") and \
       re.search(r'[\w\-]+\.(com|org|net|io|edu|gov|in|co|youtube|google|github)', low):
        if cmd_open_url(low):
            return

    # ── Apps ───────────────────────────────────────
    if contains(low, "open", "launch", "start"):
        if cmd_open_app(low):
            return

    # ── Files / Folders ────────────────────────────
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

    # ── Unknown ────────────────────────────────────
    respond(f"I don't understand: '{cmd}'. Type {BOLD}help{RESET}{GREEN} to see what I can do.", color=YELLOW)

# ─────────────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────────────
def main():
    os.system("cls")
    print_banner()
    info(f"Running on {platform.system()} {platform.release()} | Python {platform.python_version()}")
    print()

    while True:
        try:
            user_input = input(f"{GREEN}smart@terminal{RESET}:{CYAN}~{RESET}$ ").strip()
            if not user_input:
                continue
            print()
            route(user_input)
            print()
        except KeyboardInterrupt:
            print(f"\n{CYAN}  Use 'exit' to quit.{RESET}\n")
        except Exception as e:
            error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()