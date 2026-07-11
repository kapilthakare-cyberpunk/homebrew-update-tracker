# 📦 Homebrew Update Tracker

**Track every new formula and cask that lands in Homebrew — automatically, every day.**

A macOS launchd-powered pipeline that runs `brew update` daily, discovers newly added formulae and casks, fetches their descriptions, and produces a beautiful, searchable HTML dashboard for browsing what's new.

<p align="center">
  <img src="assets/screenshot.png" alt="Dashboard Screenshot" width="800" />
</p>

---

## ✨ Features

- ⏰ **Daily 9:00 AM auto-update** via `launchd` — wakes after sleep, survives reboots
- 🔍 **Live search & date filter** — instantly find tools by name, description, or use case
- 🌓 **Light & dark mode** — adapts to your system appearance automatically
- 📊 **Cumulative log** — every new discovery is saved to JSON; nothing is lost
- 🍎 **macOS native** — Apple design language, zero dependencies beyond Python 3 and Homebrew
- 🏷️ **Formulae + Casks** — tracks both CLI tools and GUI apps

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/kapilthakare-cyberpunk/homebrew-update-tracker.git
cd homebrew-update-tracker

# 2. Install the scripts
cp brew-daily-update.sh ~/.local/bin/
cp generate-homebrew-html.py ~/.local/bin/
chmod +x ~/.local/bin/brew-daily-update.sh ~/.local/bin/generate-homebrew-html.py

# 3. Initialize with your current Homebrew knowledge
echo "[]" > ~/Documents/homebrew-updates.json

# 4. Load the LaunchAgent
cp com.kapil.homebrew-daily-update.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist

# 5. Run once manually to test
bash ~/.local/bin/brew-daily-update.sh

# 6. Open the dashboard
open ~/Documents/homebrew-updates.html
```

## 📁 How It Works

```
launchd (9:00 AM daily)
    │
    ▼
brew-daily-update.sh
    │
    ├── brew update          ← fetch latest formulae/casks
    ├── Parse "New Formulae" & "New Casks" blocks
    ├── brew desc <name>     ← get description for each new item
    │
    ▼
homebrew-updates.json       ← cumulative data store
    │
    ▼
generate-homebrew-html.py   ← rebuild the HTML dashboard
    │
    ▼
homebrew-updates.html       ← open in any browser
```

## 📋 File Overview

| File | Purpose |
|---|---|
| `brew-daily-update.sh` | Main cron/launchd script — runs `brew update`, parses output, logs to JSON |
| `generate-homebrew-html.py` | Reads JSON data, generates the interactive HTML tracker |
| `com.kapil.homebrew-daily-update.plist` | macOS LaunchAgent plist — schedules daily 9:00 AM run |
| `homebrew-updates.json` | Persistent JSON log of all discovered software |

## 🛠 Managing the Job

```bash
# Check if the job is loaded
launchctl list | grep homebrew-daily

# Stop
launchctl unload ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist

# Re-enable
launchctl load ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist

# View logs
cat /tmp/homebrew-daily-update.log
```

## 🧩 Requirements

- **macOS** (launchd is macOS-only)
- **Homebrew** (obviously)
- **Python 3** (built into macOS)

## 📄 License

MIT — use it, fork it, ship it.

---

*Built for macOS power users who want to know what's new in the brew ecosystem without checking release notes every day.*
