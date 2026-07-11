# Homebrew Update Tracker

A macOS utility that records newly discovered Homebrew formulae and casks, then builds a searchable HTML table you can revisit later. It is designed for people who miss a package announcement during the day and want a simple history of new tools and apps to explore.

## What it does

- Runs `brew update` once a day with a macOS LaunchAgent.
- Detects new formulae and casks reported by Homebrew.
- Stores discoveries in a cumulative JSON file so entries are not lost.
- Generates a standalone HTML table with search and date filtering.
- Tracks both command-line packages and macOS applications.
- Supports light and dark system appearance.

## Requirements

- macOS
- Homebrew
- Python 3

## Installation

```bash
git clone https://github.com/kapilthakare-cyberpunk/homebrew-update-tracker.git
cd homebrew-update-tracker

mkdir -p ~/.local/bin
cp brew-daily-update.sh generate-homebrew-html.py ~/.local/bin/
chmod +x ~/.local/bin/brew-daily-update.sh ~/.local/bin/generate-homebrew-html.py

mkdir -p ~/Documents
printf '[]\n' > ~/Documents/homebrew-updates.json
```

Before loading the LaunchAgent, open `com.kapil.homebrew-daily-update.plist` and update the script path if your macOS username or install location differs from the example. Then run:

```bash
mkdir -p ~/Library/LaunchAgents
cp com.kapil.homebrew-daily-update.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist
bash ~/.local/bin/brew-daily-update.sh
open ~/Documents/homebrew-updates.html
```

The daily job is scheduled for 9:00 AM local time. `launchd` can run it after a missed interval when appropriate, such as after the Mac wakes from sleep.

## How it works

```text
launchd
  -> brew-daily-update.sh
  -> brew update
  -> identify new formulae and casks
  -> append discoveries to ~/Documents/homebrew-updates.json
  -> generate-homebrew-html.py
  -> ~/Documents/homebrew-updates.html
```

The JSON file is the source of truth. The HTML file is regenerated from it after each run, so you can keep the data and rebuild the dashboard whenever needed.

## Files

| File | Purpose |
| --- | --- |
| `brew-daily-update.sh` | Runs the update, identifies new packages, records descriptions, and rebuilds the dashboard. |
| `generate-homebrew-html.py` | Converts the JSON history into a searchable HTML table. |
| `com.kapil.homebrew-daily-update.plist` | Schedules the daily macOS LaunchAgent run. |
| `homebrew-updates.json` | Example data file committed with the project. Your live data is stored in `~/Documents`. |

## Managing the scheduled job

```bash
launchctl list | grep homebrew-daily
launchctl unload ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist
launchctl load ~/Library/LaunchAgents/com.kapil.homebrew-daily-update.plist
cat /tmp/homebrew-daily-update.log
cat /tmp/homebrew-daily-update.err
```

## Notes

- The current parser depends on the `brew update` output headings `New Formulae` and `New Casks`.
- The included LaunchAgent uses an example absolute path; update it for your account before installation.
- The repository does not include a license yet. Add one if you intend others to reuse or distribute the project.

## License

No license has been declared yet.
