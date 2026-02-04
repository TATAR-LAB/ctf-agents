# Experiment Guide: RQ1 & RQ2

This guide lists the configuration files created for testing Research Questions 1 (Infrastructure) and 2 (Prompt Engineering).

## Experimental Design (2x2x2)

We are testing 8 conditions based on three variables:

1. **Infrastructure:** Ubuntu (Baseline) vs. Kali Linux (Treatment)
2. **Prompts:** Generic (No Tips) vs. Specialized (With Tips)
3. **AutoPrompt:** Disabled vs. Enabled

## Configuration Map

| Condition | Description                      | Config File                                                    |
| --------- | -------------------------------- | -------------------------------------------------------------- |
| **1**     | Ubuntu + Generic + No AutoPrompt | `configs/tatar-project/RQ1_RQ2/ubuntu_generic.yaml`            |
| **2**     | Ubuntu + Generic + AutoPrompt    | `configs/tatar-project/RQ1_RQ2/ubuntu_generic_autoprompt.yaml` |
| **3**     | Ubuntu + Tips + No AutoPrompt    | `configs/tatar-project/RQ1_RQ2/ubuntu_tips.yaml`               |
| **4**     | Ubuntu + Tips + AutoPrompt       | `configs/tatar-project/RQ1_RQ2/ubuntu_tips_autoprompt.yaml`    |
| **5**     | Kali + Generic + No AutoPrompt   | `configs/tatar-project/RQ1_RQ2/kali_generic.yaml`              |
| **6**     | Kali + Generic + AutoPrompt      | `configs/tatar-project/RQ1_RQ2/kali_generic_autoprompt.yaml`   |
| **7**     | Kali + Tips + No AutoPrompt      | `configs/tatar-project/RQ1_RQ2/kali_tips.yaml`                 |
| **8**     | Kali + Tips + AutoPrompt         | `configs/tatar-project/RQ1_RQ2/kali_tips_autoprompt.yaml`      |

## Prompt Details

### Generic Prompts (Control)

- **Files:** `prompts/ubuntu_generic_*.yaml`, `prompts/kali_generic_*.yaml`
- **Content:** Standard role definition and challenge description.
- **Removed:** All "IMPORTANT TIPS" sections (e.g., about using pwntools, hexdump).

### Specialized Prompts (Treatment)

- **Files:** `../../dcipher/prompts/base_*.yaml` (for Ubuntu), `prompts/kali_tips_*.yaml` (for Kali)
- **Content:** Includes "IMPORTANT TIPS" section.
- **Kali Extensions:** Adds specific guidance on using `list_commands` and `lookup_command` tools.

## Running Experiments

Run any condition using:

```bash
uv run run_dcipher.py --config configs/tatar-project/RQ1_RQ2/<CONFIG_FILE> \
  --split development --challenge "2016q-for-kill" --keys ./keys.cfg
```


---


# RQ1: Infrastructure — Does enhanced security tooling improve results?

## Hypothesis
H1.1: Providing LLMs with access to a comprehensive set of penetration testing tools 
will improve solve rates compared to the baseline Ubuntu environment.

## Experiment Conditions

| Condition | Environment | Extra Tools |
|-----------|-------------|-------------|
| Baseline  | Ubuntu Docker | - |
| Treatment | Kali Linux Docker | `list_commands`, `lookup_command` |

## Setup (One-time)

### Build the Kali Docker Image

```bash
cd docker/kali
docker build -t ctfenv:kali .
```

## Kali Tool Discovery Tools

The Kali config includes two tools for discovering and learning about available security tools:

### `list_commands` - List all available tools

```python
# Lists all commands with brief descriptions
list_commands()
```

Output:
```
## Network
- nmap - Network exploration and security auditing
- masscan - High-speed internet port scanner
- curl - Transfer data with URLs
...

## Web
- sqlmap - Automatic SQL injection tool
- nuclei - Template-based vulnerability scanner
...
```

### `lookup_command` - Get detailed documentation

```python
# Get detailed docs for a specific tool
lookup_command(command="nmap")
```

Output includes: description, usage syntax, options, and examples.

## Available Tools (74)

The documentation in `docker/kali/commands_documentation.csv` covers tools verified from `vxcontrol/kali-linux`:

- **Network (13)**: nmap, masscan, netcat, nc, ncat, curl, wget, tcpdump, tshark, amass, subfinder, httpx, theharvester
- **Web (13)**: sqlmap, nikto, gobuster, dirb, wfuzz, nuclei, ffuf, feroxbuster, katana, dirsearch, whatweb, wpscan, commix
- **Windows/AD (11)**: crackmapexec, netexec, evil-winrm, responder, impacket-secretsdump, impacket-psexec, impacket-smbclient, bloodhound-python, smbmap, smbclient, enum4linux
- **Reversing (9)**: gdb, radare2, strings, objdump, ltrace, strace, checksec, ropper, ROPgadget
- **Forensics (7)**: binwalk, foremost, steghide, exiftool, file, xxd, hexdump
- **General (7)**: grep, find, awk, sed, python3, pwntools, rlwrap
- **Password (6)**: john, hashcat, hydra, medusa, crunch, hashid
- **Exploitation (3)**: msfconsole, msfvenom, searchsploit
- **Tunneling (3)**: chisel, proxychains4, socat
- **Crypto (2)**: base64, openssl

## Notes
- Both configs use the **same dcipher prompts** for fair infrastructure comparison
- Kali config includes tool discovery tools (`list_commands`, `lookup_command`)
- The `kali_docker.yaml` config has `use_kali: True` which automatically selects the Kali image

---

# RQ2: Prompt Engineering — Do the "IMPORTANT TIPS" help?

## Hypothesis
H2.1: The "IMPORTANT TIPS" section in the prompts improves solve rates by providing 
actionable guidance (use pwntools, hexdump, disassemble tools, avoid interactive interfaces).

## What's Being Tested

The **only difference** between conditions is the "IMPORTANT TIPS" section in the `initial` prompt:

### Executor Tips (removed in generic)
```
IMPORTANT TIPS:

  - You are an autonomous agent and you should complete the task by yourself...
  - Write python scripts with `pwntools` to pass inputs to local programs...
  - Use `hexdump` to parse binary data instead of dumping it raw.
  - Try to use the provided `disassemble` and `decompile` tools...
  - Write scripts to run commands like `gdb` or `r2`...
  - REMEMBER! You can finish the task and solve the challenge by yourself...
```

### Planner Tips (removed in generic)
```
IMPORTANT TIPS:

  - You are an autonomous agent and you should complete the challenge...
  - Provide specific information in the task description like file names...
  - REMEMBER! You can plan and solve the challenge without my help...
```

## Experiment Conditions

| Condition | Prompts |
|-----------|---------|
| A (Treatment) | With IMPORTANT TIPS |
| B (Control) | Without IMPORTANT TIPS |

## Notes
- Both use identical system prompts, initial prompts, continue prompts, etc.
- Only the "IMPORTANT TIPS" section is removed in the generic condition
- Same model (Gemini 3 Pro/Flash) for fair comparison
