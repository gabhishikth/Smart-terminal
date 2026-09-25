# 🤖 Smart Terminal Assistant

> **An AI-powered, voice-enabled Windows terminal assistant that combines system automation, natural-language interaction, speech recognition, text-to-speech, and LLM capabilities.**

---

## 📌 Overview

**Smart Terminal** is an intelligent command-line assistant designed to make computer interaction more natural and powerful.

Instead of relying only on traditional terminal commands, users can interact with the system using:

* ⌨️ Natural-language text commands
* 🎤 Voice commands
* 🤖 AI-powered conversations, with real tool execution
* 🔊 Text-to-speech responses
* 🖥️ Windows system operations
* 📁 File and folder management
* 🌐 Web search and website navigation
* 🌦️ Weather information
* 🧮 Calculations
* 🚀 Application launching

The project is being developed progressively toward a full **AI-powered voice agent** capable of understanding natural language, executing tools, searching external services, diagnosing errors, interacting with APIs, and communicating conversationally.

---

# 🎯 Project Objectives

1. Build a natural-language interface for a Windows computer.
2. Enable voice-based interaction with the terminal.
3. Integrate an LLM for conversational intelligence.
4. Execute real system operations through controlled functions.
5. Add intelligent error detection and correction.
6. Integrate external APIs and services.
7. Support applications such as YouTube, Spotify, email, search, etc.
8. Add multilingual speech recognition.
9. Implement semantic search and RAG.
10. Evolve the project into an AI agent capable of using multiple tools.

---

# 🏗️ Current Architecture

```text
                         USER
                          │
             ┌────────────┴────────────┐
             │                         │
          Keyboard                  Microphone
             │                         │
             │                   Speech-to-Text
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
                  Smart Terminal
                          │
                  Command Router
                          │
             ┌────────────┴────────────┐
             │                         │
       Known command              Unknown input
             │                         │
             ▼                         ▼
      Python Handlers            Gemini (with tools)
             │                         │
             ▼                         ▼
      System / File / App      Chat, or a real tool call
      / Web / Weather          (opens apps, files, sites,
             │                  checks weather, math, etc.)
             └────────────┬────────────┘
                          │
                          ▼
                    Text Response
                          │
                          ▼
                     Text-to-Speech
                          │
                          ▼
                         🔊
```

The router handles known commands deterministically — fast, free, no AI involved. Unrecognized input goes to Gemini, which can either reply conversationally or **call a real Python function** to actually do something, verify it worked, and reply based on the true outcome.

---

# ✨ Current Features

## 🎤 Voice Interaction

Uses `SpeechRecognition` + `PyAudio` to listen through the default microphone and convert speech into text before processing it — no hard cap on how long you can talk; it stops on a natural pause, not a fixed duration.

```text
User: "Open Chrome"
Speech → Speech-to-Text → "open chrome" → Command Router → Chrome opens
```

## 🔊 Text-to-Speech

Uses `pyttsx3` (offline, via Windows SAPI5) so the assistant can respond both visually and audibly — including AI-generated replies, not just built-in command confirmations.

---

# 🖥️ Supported Terminal Operations

### 🌐 Browser & Web
```text
open browser / open chrome / open firefox / open edge
open youtube.com
search python tutorials
google what is AI
```

### 📁 Files & Folders
```text
open file notes.txt
open folder Downloads
C:\Users\you\file.txt        (full path, no keyword needed)
open report.docx             (bare name — searches common folders automatically)
create file test.txt
create folder MyFolder
delete file test.txt
list files
list folder Downloads
```

### 🖥️ Applications
```text
open notepad / open calculator / open VLC / open Spotify
open Word / open Excel / open VS Code
```

### ⚙️ System Operations
```text
shutdown / restart / lock / sleep
screenshot
volume up / volume down / mute / unmute
battery
```

### 🕒 Date and Time
```text
what time is it
what is today's date
```

### 🧮 Mathematics
```text
calculate 25 * 48
what is 100 / 4
```

### 📋 Clipboard
```text
copy Hello World
paste
```

### 🌦️ Weather
```text
weather
weather in Chennai
```

### 🎲 Utility / Fun
```text
tell me a joke
flip a coin
roll a dice
random number 1 100
```

### 💻 Arbitrary Commands
```text
run notepad.exe
run <command>
```

---

# 🤖 Gemini Integration & Function Calling

Gemini acts as the fallback when input doesn't match a predefined local command — and it's not limited to chatting. It can **call real functions** in the codebase to actually do things.

```text
User Input
    ↓
Command Router
    ↓
Known command?
 ┌──┴───┐
 YES    NO
 │       │
 ▼       ▼
Python  Gemini
 │       │
 │   ┌───┴────┐
 │   │        │
 │   ▼        ▼
 │  Chat   Tool call
 │           │
 │           ▼
 │    Real action + honest
 │    result reported back
 │           │
 └─────┬─────┘
       ▼
    Response
```

Uses Google's `google-genai` Python SDK, model `gemini-3.5-flash`, loaded via the `GEMINI_API_KEY` environment variable.

## ✅ Implemented Tools (Phase 4.1 — Safe Tools)

| Tool | What it does |
|---|---|
| `tool_open_application(app_name)` | Opens a Windows app by name — checks real install paths for browsers before claiming success |
| `tool_open_website(site)` | Opens a website by name or URL — `youtube` → `https://youtube.com` |
| `tool_open_file_or_folder(name)` | Opens a file/folder by name, searching common folders if no full path is given |
| `tool_get_weather(city)` | Current weather via wttr.in |
| `tool_calculate(expression)` | Evaluates a math expression |
| `tool_tell_joke()` | Random programming joke |
| `tool_get_current_time()` / `tool_get_current_date()` | Current time/date |
| `tool_get_battery_status()` | Battery percentage and charging state |

Every tool **verifies its action actually succeeded before reporting success** — e.g. checking `shutil.which()` or known install paths rather than trusting a subprocess call blindly. A tool that silently claims success when nothing happened would let Gemini confidently tell the user something false.

## 🔜 Not Yet Tools — Still Planned

* **Phase 4.2 — Media:** `search_youtube()`, `play_spotify_song()`, `pause_media()`, etc.
* **Phase 4.3 — Communication:** `generate_email()`, `send_email()`
* **Phase 4.4 — More system tools:** `volume_up()`, `volume_down()`, `lock_computer()`

## ⚠️ Deliberately Excluded From Tools

`shutdown`, `restart`, `delete file`, and `run` (arbitrary command execution) are **never** exposed to Gemini as callable tools. They remain keyword-only in the router, gated behind their existing yes/no confirmation. An LLM should never have a direct path to destructive system actions — this is a firm design boundary, not a temporary gap.

---

# 🧠 Why Gemini Is Important

A purely rule-based router struggles with the sheer number of ways people phrase the same request:

```text
Open Spotify / Launch Spotify / Start Spotify /
Can you open Spotify? / I'd like to listen to music.
```

Function calling lets Gemini extract intent from any of these phrasings and call the same underlying tool — without needing a keyword branch for every possible wording.

---

# 🚀 Development Roadmap

The project is built sequentially — each version keeps everything from the version before it working.

| Version | Focus | Status |
|---|---|---|
| V1 | Basic rule-based terminal | ✅ Completed |
| V2 | Voice input + TTS | ✅ Completed |
| V3 | Gemini conversational fallback | ✅ Completed |
| V4 | Function calling (safe tools) | ✅ Completed |
| V5 | Intelligent error detection | 🔜 Planned |
| V6 | NLP concepts (intent, entities, embeddings) | 🔜 Planned |
| V7 | Semantic search | 🔜 Planned |
| V8 | RAG (retrieval-augmented generation) | 🔜 Planned |
| V9 | External APIs (YouTube, Spotify, email, GitHub) | 🔜 Planned |
| V10 | Multilingual speech (Whisper / Wav2Vec2) | 🔜 Planned |
| V11 | Full conversational AI agent | 🔜 Final goal |

### V5 — Intelligent Error Detection (next up)

Goal: understand errors instead of just displaying them.

```text
Current:  Command → Error → Display error
Future:   Command → Error → Classify → Diagnose → Suggest fix → Confirm → Apply
```

Planned approach: start simple (pipe caught exceptions to Gemini for a plain-language explanation), then layer in an embeddings-based lookup of previously-seen errors and their solutions — a personal, growing knowledge base of this specific project's quirks, faster and cheaper than an LLM call for errors already solved once.

### V9 — Multilingual Speech, model choice

`Wav2Vec2` fine-tuned on LibriSpeech is English-only; going multilingual means either a different Wav2Vec2 checkpoint (`wav2vec2-large-xlsr-53`) or switching to **Whisper**, which supports 99 languages out of the box — the more direct path for this specific goal.

---

# 🧰 Technology Stack

| Category | Libraries |
|---|---|
| Voice | `SpeechRecognition`, `PyAudio` |
| Text-to-Speech | `pyttsx3` |
| AI | `google-genai` (Gemini API) |
| System automation | `subprocess`, `os`, `webbrowser`, `ctypes`, `shutil` |
| Utilities | `requests`, `pyperclip`, `Pillow`, `psutil`, `python-dotenv` |
| Config | `.env` via `python-dotenv` |

Several of these are conditionally imported, so optional functionality (voice, clipboard, weather) degrades gracefully rather than crashing if a package isn't installed.

---

# 📦 Installation

### 1. Clone the repository
```bash
git clone <YOUR_REPOSITORY_URL>
cd smart-terminal
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Gemini
Create a `.env` file (copy `.env.example`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Never commit this file to GitHub.

### 5. Run
```bash
python smart_terminal.py
```

---

# 🚫 .gitignore

```gitignore
# Environment variables
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

---

# 📁 Recommended Future Project Structure

The current single-file implementation should eventually split into modules as it grows:

```text
smart-terminal/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── src/
│   ├── main.py
│   ├── core/          (router, config, logger)
│   ├── voice/          (speech_to_text, text_to_speech)
│   ├── ai/             (gemini client, tool definitions, prompts)
│   ├── tools/           (files, apps, browser, weather, youtube, spotify, email)
│   ├── rag/             (embeddings, retriever, vector_store)
│   └── utils/
├── tests/
└── docs/
```

Introduce this structure gradually — not all at once.

---

# 🛡️ Security Considerations

* **Never commit `.env`** — API keys live in environment variables only.
* **Never let an LLM run arbitrary shell commands** — no `subprocess.run(llm_generated_command, shell=True)`.
* **Destructive operations require explicit confirmation**: delete, shutdown, restart, format, email sending.
* **Validate function arguments** against known-safe values (e.g. app names against an allowed list) before acting on them.
* **A confident-sounding tool result isn't automatically a true one** — every tool should verify its action actually succeeded before reporting success back to the model.

---

# 📊 Error Handling Philosophy

The system should never crash because a microphone is missing, speech recognition fails, Gemini is unreachable, a file doesn't exist, an app isn't installed, or the internet is down. Every failure path should be caught, explained in plain language, and — eventually — paired with a suggested fix (V5).

---

# 🧠 Learning Requirements

**Python:** functions, classes, exception handling, subprocess, APIs, JSON, environment variables
**NLP:** tokenization, intent classification, entity extraction, embeddings, semantic search
**LLM:** prompting, chat/context, function calling, structured output, agent architecture
**RAG:** embeddings, vector databases, chunking, retrieval
**Speech AI:** Wav2Vec2, Whisper, multilingual STT, TTS
**APIs:** REST, OAuth, rate limits

---

# 📈 Future Vision

> *"Search YouTube for a good Wav2Vec2 tutorial, open the first result, and create a folder called Speech Project."*

> *"My Python project is showing a module error. Find out what's wrong and tell me how to fix it."*

The long-term goal: a secure, extensible, multilingual, AI-powered terminal that understands natural language, reasons about requests, retrieves knowledge, uses tools, talks to external services, and automates computer tasks through voice or text — with the user always in control of anything destructive.

---

## 📜 License

MIT License (or your chosen license)

---

## ⭐ Project Status

**Active development.**

**Current milestone:** Function calling complete (9 tools) → next up: Intelligent error detection (V5)
