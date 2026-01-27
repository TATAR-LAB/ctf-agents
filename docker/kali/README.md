# Kali Linux Docker Image for D-CIPHER

This Docker image provides a Kali Linux environment with pre-installed penetration testing tools for CTF challenge solving.

## Build Instructions

```bash
# Navigate to the kali directory
cd docker/kali

# Build the image (tag as ctfenv:kali)
docker build -t ctfenv:kali .

# For Apple Silicon (ARM), the base image should work but may be slower
docker build -t ctfenv:kali .
```

## Usage

### Via Config File

Add `use_kali: True` to your experiment config:

```yaml
experiment:
  max_cost: 1.0
  enable_autoprompt: False
  use_kali: True  # This enables Kali Linux environment
```

### Via Command Line

Override with `--use-kali` flag:

```bash
uv run run_dcipher.py \
  --config configs/tatar-project/RQ1-infrastructure/ubuntu_baseline.yaml \
  --use-kali \
  --challenge "2016q-for-kill"
```

## Pre-installed Tools

### Network
- nmap, netcat, tcpdump, masscan

### Web Security  
- sqlmap, nikto, gobuster, dirb, wfuzz

### Password Cracking
- john, hashcat, hydra, medusa

### Forensics
- binwalk, foremost, steghide, exiftool, sleuthkit, volatility3(?)

### Reverse Engineering
- gdb, radare2, Ghidra (with custom scripts)

### Crypto
- openssl, gpg

### Python Libraries
- pwntools, angr, chepy, z3-solver, gmpy2

## Comparison with Ubuntu Image

| Feature | Ubuntu (ctfenv:multiagent) | Kali (ctfenv:kali) |
|---------|---------------------------|-------------------|
| Base OS | Ubuntu 22.04 | Kali Linux |
| Pentest Tools | Limited | Comprehensive |
| Image Size | ~2GB | ~4GB |
| Build Time | ~10 min | ~15 min |
