<h1 align="center">
  <br>
  <pre>
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ███████╗███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  ██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║     ███████╗██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝
  </pre>
  <br>
  Autopen
</h1>

<h4 align="center">A fully autonomous AI-driven penetration testing framework powered by <a href="https://ollama.com">Ollama</a> and <a href="https://langchain.com">LangChain</a>.</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/LangChain-0.3.25-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Model-qwen2.5:3b-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-purple?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-red?style=flat-square" />
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#modes">Modes</a> •
  <a href="#output">Output</a> •
  <a href="#disclaimer">Disclaimer</a>
</p>

---

## Overview

Autopen is a final year project that demonstrates the application of Large Language Models (LLMs) to autonomous offensive security. It uses a **LangChain ReAct agent** to autonomously plan, execute, and chain penetration testing tools — from initial recon all the way through to exploitation and report generation — with zero human intervention during the engagement.

The agent runs entirely **offline** using `qwen2.5:3b` via Ollama, making it suitable for air-gapped and privacy-sensitive environments.

---

## Features

- **Fully Autonomous** — AI plans and executes the entire pentest lifecycle without human input
- **ReAct Agent** — Reasoning + Acting loop: thinks before every tool call, adapts based on results
- **Step Memory** — Tracks completed actions live, prevents tool repetition and infinite loops
- **4 Engagement Modes** — Web, Network, Full, and CTF
- **CTF Mode** — Aggressive flag-hunting mode with higher creativity, designed for CTF challenges
- **14 Integrated Tools** — Covering recon, scanning, exploitation, and post-exploitation
- **Structured Reports** — Auto-generates Markdown report + JSON log after every engagement
- **Offline LLM** — Fully local inference via Ollama, no data leaves your machine

---

## Architecture

```
User (CLI)
    │
    ▼
autopen.py  ──── argparse CLI ──── config.yaml
    │
    ▼
agent/core.py  ──── LangChain ReAct Agent
    │                    │
    │              LiteLLM / OllamaLLM
    │                    │
    │              qwen2.5:3b (local)
    │
    ├── agent/memory.py     ← Step memory (prevents looping)
    ├── agent/tools.py      ← All pentest tools as LangChain Tools
    └── agent/summariser.py ← Trims tool output for context window
    │
    ▼
Tool Executor (subprocess)
    │
    ├── Recon:       whois, theHarvester, subfinder
    ├── Scanning:    nmap, whatweb, feroxbuster, nikto
    ├── Vuln:        searchsploit
    ├── Exploit:     sqlmap, hydra, metasploit
    └── Post-Exploit: linpeas, netcat
    │
    ▼
report/generator.py
    │
    ├── outputs/<target>_<timestamp>.md   ← Markdown report
    └── outputs/<target>_<timestamp>.json ← JSON engagement log
```

---

## Installation

### Prerequisites

- Kali Linux (recommended)
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- The following tools installed: `nmap`, `nikto`, `sqlmap`, `feroxbuster`, `theharvester`, `subfinder`, `hydra`, `metasploit-framework`, `searchsploit`

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/mrprice-sec/autopen.git
cd autopen

# 2. Install Python dependencies
pip install -r requirements.txt --break-system-packages

# 3. Pull the AI model
ollama pull qwen2.5:3b

# 4. Install missing tools (Kali)
sudo apt install -y feroxbuster theharvester exploitdb subfinder
```

---

## Usage

```bash
python3 autopen.py --target <target> --mode <mode> [--verbose]
```

### Arguments

| Argument | Description |
|---|---|
| `--target` | Target IP, domain, URL, or CIDR range |
| `--mode` | Engagement mode: `web`, `network`, `full`, `ctf` |
| `--verbose` | Show live agent reasoning (Thought/Action/Observation) |
| `--config` | Path to config file (default: `config.yaml`) |

### Examples

```bash
# Web application pentest
python3 autopen.py --target http://target.com --mode web --verbose

# Network pentest
python3 autopen.py --target 192.168.1.0/24 --mode network

# Full engagement (web + network)
python3 autopen.py --target 192.168.1.50 --mode full --verbose

# CTF challenge — aggressive flag hunting
python3 autopen.py --target http://10.10.10.5 --mode ctf --verbose
```

---

## Modes

| Mode | Description | Aggression |
|---|---|---|
| `web` | Standard web application pentest. Covers recon, directory enumeration, web vulnerability scanning and SQLi. | Medium |
| `network` | Network/host pentest. Host discovery, port scanning, service exploitation. | Medium |
| `full` | Combined web + network engagement. | Medium |
| `ctf` | Aggressive CTF flag-hunting mode. Agent is framed as a CTF competitor hunting a hidden flag. Higher temperature, more creative exploitation chains. | Maximum |

---

## Output

After every engagement, Autopen saves two files to `outputs/`:

**Markdown Report** (`<target>_<timestamp>.md`)
```
# Autopen Penetration Test Report
## Engagement Details
## Executive Summary
## Tool Execution Log
## Disclaimer
```

**JSON Log** (`<target>_<timestamp>.json`)
```json
{
  "target": "http://target.com",
  "mode": "web",
  "timestamp": "20260310_064450",
  "steps": [...],
  "final_output": "..."
}
```

---

## Project Structure

```
autopen/
├── autopen.py              # CLI entry point
├── config.yaml             # Model and tool configuration
├── requirements.txt
├── agent/
│   ├── core.py             # LangChain ReAct agent + CTF/pentest prompts
│   ├── tools.py            # All pentest tool definitions
│   ├── memory.py           # Step memory — prevents agent looping
│   └── summariser.py       # Trims tool output for context window
├── report/
│   └── generator.py        # Markdown + JSON report builder
├── phases/                 # Phase modules (extensible)
└── outputs/                # Engagement reports saved here
```

---

## Configuration

Edit `config.yaml` to change the model or tweak agent behaviour:

```yaml
model:
  provider: ollama
  name: qwen2.5:3b        # Change to any Ollama model
  base_url: http://localhost:11434

agent:
  max_iterations: 25       # Max agent steps per engagement
  verbose: false           # Set true to always show reasoning

output:
  dir: outputs/
```

---

## Disclaimer

> Autopen is developed for educational and research purposes as a final year project.
> Only use against systems you own or have explicit written permission to test.
> The author is not responsible for any misuse or damage caused by this tool.
> Unauthorized penetration testing is illegal.

---

## Author

**Odigili Treasure C.** — [@mrprice-sec](https://github.com/mrprice-sec)

*Final Year Project — Autonomous AI-Driven Penetration Testing*
