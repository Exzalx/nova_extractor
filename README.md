# 🌌 NOVA EXTRACTOR

### *Ultimate Web Crawler & Data Extractor for Termux/Linux*

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20Android-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Developer](https://img.shields.io/badge/Developer-BgxHost-orange)

---

## 🛡️ Legal Disclaimer
> **WARNING:** This tool is strictly for **educational, research, and authorized testing purposes only**. 
> The developer (`BgxHost`) is not responsible for any misuse, data harvesting, or illegal activities performed using this tool. 
> Always respect `robots.txt`, obtain proper authorization before scanning any target, and comply with local laws. **Stay Ethical, Stay Legal.**

---

## 🚀 Features

### ⚡ Core Engine
- **No Playwright Required:** Pure Python `aiohttp` based, making it 100% compatible with Termux and low-end Android devices.
- **Mass Async Crawling:** Scan hundreds of pages simultaneously using configurable concurrent Python workers.
- **Smart Deduplication:** Memory-efficient Bloom Filter to prevent duplicate URL processing.
- **Intelligent Rate Limiting:** Token bucket algorithm to prevent server overload and IP bans.
- **Auto-Retry & Recovery:** Exponential backoff retry mechanism for failed requests.

### 📊 Advanced Data Extraction
- **Contact Harvesting:** Auto-extract Email addresses and International Phone numbers using smart Regex.
- **SEO Meta Data:** Extract Page Titles, Meta Descriptions, Keywords, and H1 tags.
- **Deep Link Discovery:** Parses `href`, `src`, and `action` attributes recursively with depth control.

### 🔐 Session & Access Management
- **Login Support:** Automated form submission with CSRF token extraction.
- **Cookie Handling:** Supports both raw cookie strings and JSON file imports.
- **Proxy Support:** Route traffic through HTTP/HTTPS proxies for anonymity.

### 💾 Storage & Export
- **SQLite Database:** Persistent, crash-resistant local storage (`crawler.db`).
- **Multi-Format Export:** One-click export to `JSON`, `CSV`, `TXT`, and human-readable `Summary Reports`.
- **Graceful Interruption:** Pressing `Ctrl+C` safely saves all partial results before exiting.

---

## 📦 Installation & Requirements

### ⚡ One-Command Installation (Recommended for Termux)
Copy and paste this single command to install everything automatically:
```bash
pkg update && pkg upgrade -y && pkg install python git -y && git clone https://github.com/BgxHost/nova_extractor.git && cd nova_extractor && pip install -r requirements.txt && clear && python nova_extractor.py
```

### 📱 Manual Installation (Termux / Android)
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/BgxHost/nova_extractor.git
cd nova_extractor
pip install -r requirements.txt
python nova_extractor.py
```

### 🐧 Linux (Debian/Ubuntu/Kali)
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3 python3-pip git
git clone https://github.com/BgxHost/nova_extractor.git
cd nova_extractor
pip3 install -r requirements.txt
python3 nova_extractor.py
```

### 📋 Requirements (`requirements.txt`)
The tool relies on minimal dependencies. The `requirements.txt` file contains:
```text
aiohttp>=3.9.0
async-timeout>=4.0.0
charset-normalizer>=3.0.0
attrs>=23.0.0
frozenlist>=1.4.0
msgpack>=1.0.0
multidict>=6.0.0
yarl>=1.9.0
```
*(Note: If `pip install -r requirements.txt` fails, run: `pip install aiohttp`)*

---

## 📖 Usage Guide

### 1️⃣ Running the Tool
To start the interactive panel interface, simply run:
```bash
python nova_extractor.py
```
*(Upon startup and exit, the tool will automatically prompt/open the official Telegram channel.)*

### 2️⃣ Quick Crawl (Free Mode)
1. Select **`[1] Start Crawling (Quick Mode)`** from the Main Menu.
2. Enter your target URL (e.g., `https://example.com`).
3. Confirm with `y`. The tool will crawl up to the default depth (3) and save results to `crawl_output/`.

### 3️⃣ Crawl with Login (Session Mode)
1. Select **`[2] Crawl with Login`**.
2. Provide the target dashboard URL and the login page URL.
3. Enter the username/password field names (e.g., `email`, `password`) and your credentials.
4. *(Optional)* Paste browser cookie strings for persistent sessions.
5. The tool will authenticate and crawl the protected areas.

### 4️⃣ Advanced Configuration
1. Select **`[5] Configure Settings`** to modify:
   - Max Crawl Depth (Default: 3)
   - Max Pages (Default: 1000)
   - Concurrent Workers (Default: 10)
   - Request Delay (Default: 1.0s)
   - Proxy Settings

---

## 📂 Output Files
All extracted data is neatly organized in the `crawl_output/` directory:
- 📄 `crawl_results.json` : Complete structured data.
- 📊 `crawl_results.csv` : Spreadsheet-compatible format.
- 🔗 `all_urls.txt` : Clean list of all discovered URLs.
- 📝 `summary.txt` : Human-readable report with titles and stats.

---

## ⚙️ Tool Settings & Support

- **View Database:** Use option `[6]` in the main menu to preview crawled URLs directly in the terminal.
- **Clear Data:** Use option `[7]` to safely wipe the SQLite database and output folder.
- **Support & Updates:** Join our official Telegram community for tool updates, support, and discussions:
  - **Official Channel:** [t.me/CardSELLER789](https://t.me/CardSELLER789)
  - **Developer:** [BgxHost](https://t.me/BgxHost)

---

## 📜 Copyright & License

```text
Copyright (c) 2026 BgxHost. All rights reserved.

This software and its associated documentation are the property of BgxHost. 
While distributed under the MIT License for educational use, unauthorized 
copying, malicious modification, reverse engineering, or use for illegal 
data harvesting is strictly prohibited. 

The developer assumes no liability for any damages or legal consequences 
arising from the misuse of this software. Use at your own risk.

Developed with ❤️ by BgxHost
```

---
*Optimized for Termux & Linux Environments.*
