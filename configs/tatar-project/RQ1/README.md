# RQ1: Infrastructure — Does enhanced security tooling improve results?

## Hypothesis
H1.1: Providing LLMs with access to a comprehensive set of penetration testing tools 
will improve solve rates compared to the baseline Ubuntu environment.

## Experiment Conditions

| Condition | Environment | Extra Tools | Config File |
|-----------|-------------|-------------|-------------|
| Baseline  | Ubuntu Docker | - | `ubuntu_baseline.yaml` |
| Treatment | Kali Linux Docker | `lookup_command` | `kali_docker.yaml` |

## Setup (One-time)

### Build the Kali Docker Image

```bash
cd docker/kali
docker build -t ctfenv:kali .
```

## The `lookup_command` Tool

The Kali config includes a `lookup_command` tool that allows the agent to query documentation for security tools:

```python
# Look up a specific command
lookup_command(query="nmap")

# List all available commands
lookup_command(query="list")

# List commands by category
lookup_command(query="network")  # or "web", "crypto", "forensics", "password", "reversing"
```

The documentation is stored in `docker/kali/commands_documentation.csv` and includes:
- **Network**: nmap, netcat, curl, wget, tcpdump, tshark
- **Web**: sqlmap, nikto, gobuster, dirb, wfuzz
- **Password**: john, hashcat, hydra, medusa
- **Forensics**: binwalk, foremost, steghide, exiftool, volatility3, sleuthkit
- **Reversing**: gdb, radare2, ghidra, strings, objdump, ltrace, strace
- **Crypto**: base64, openssl, z3
- **General**: grep, find, awk, sed, python3, pwntools

## Notes
- Both configs use the **same dcipher prompts** for fair infrastructure comparison
- Kali config includes `lookup_command` tool for accessing tool documentation
- The `kali_docker.yaml` config has `use_kali: True` which automatically selects the Kali image

## Usage

```bash
# Baseline (Ubuntu) - uses ctfenv:multiagent
uv run run_dcipher.py --config configs/tatar-project/RQ1/ubuntu_baseline.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg

# Treatment (Kali) - uses ctfenv:kali (must build first)
uv run run_dcipher.py --config configs/tatar-project/RQ1/kali_docker.yaml \
  --challenge "2016q-for-kill" --keys ./keys.cfg
```
