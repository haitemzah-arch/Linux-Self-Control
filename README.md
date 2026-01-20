# Linux-Self-Control
"An advanced, system-level digital wellbeing guardian for Linux. Monitors keystrokes, clipboard, and mouse selection to prevent access to harmful content and enforce system integrity."
# 🛡️ Linux Self-Control Guardian

**A powerful, aggressive, and intelligent system guardian designed to enforce digital wellbeing and prevent access to harmful content on Linux systems.**

## 🚀 Overview

This tool is not just a simple blocker. It is a comprehensive system integrity monitor designed for users who need strict self-control. It runs in the background, monitoring all input methods (Keyboard, Clipboard, Primary Selection) and enforcing critical system configurations (DNS, Network, Hosts) using immutable file attributes.

It is designed to be **hard to bypass** and **hard to kill**.

## ✨ Key Features

- **Real-time Monitoring:**
  - ⌨️ **Keystroke Logging:** Detects banned words instantly (even before you hit enter).
  - 📋 **Clipboard & Mouse Selection:** Monitors `Ctrl+C` and Middle-Click selections (using `xsel`).
  - 🧠 **Anti-Cheat Engine:** Detects "Leet Speak" (e.g., `w0rd`), repetition (e.g., `wooooord`), and spacing hacks.

- **🌍 Multi-Language Support:**
  - Full support for **Arabic** & **English**.
  - **Ghost Typing Detection:** Detects Arabic words typed on an English keyboard layout (e.g., typing `fkj` is detected as `بنت`).

- **🔒 System Lockdown:**
  - Locks critical files (`resolv.conf`, `hosts`, `netplan`) using `chattr +i`.
  - Prevents network tampering and DNS bypass.
  - Prevents killing the process via terminal (detects `kill`, `pkill`, `rm` commands).

- **⚡ Active Defense:**
  - Instantly closes the active window upon detection of any banned content.
  - Clears clipboard history immediately.

## 🛠️ Requirements

- Python 3.x
- Ubuntu / Debian based systems (X11 environment recommended).
- Root privileges (for file locking).

### Dependencies:
```bash
sudo apt install xsel xdotool e2fsprogs
pip3 install pynput pyperclip
