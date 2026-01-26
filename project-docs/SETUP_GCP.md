# GCP Setup Guide

> This guide walks you through setting up a GCP Compute Engine instance for running CTF agent experiments using SUNY workforce identity federation.

---

## 1. Authentication

Authenticate with GCP using workforce identity federation.

### Create Login Configuration
[Install --> gcloud](https://docs.cloud.google.com/sdk/docs/install-sdk#windows) 

```bash
# Generate a login config file for workforce identity pool
gcloud iam workforce-pools create-login-config \
  locations/global/workforcePools/suny-wfif-pool-glb/providers/suny-wfif-pvdr-glb \
  --output-file=gcloud.json
```

### Login to GCP

```bash
# Authenticate your user account
gcloud auth login --login-config=gcloud.json

# Set up Application Default Credentials (required for API access)
gcloud auth application-default login --login-config=gcloud.json
```

---

## 2. Connect to the Instance

SSH into the Compute Engine instance with port forwarding for Jupyter notebooks.

```bash
# SSH with port forwarding (maps remote 8080 → local 8080)
gcloud compute --project "alb-prj-utatar-sbx" ssh \
  --zone "us-central1-a" \
  "instance-20260112-153532" \
  -- -L 8080:localhost:8080
```

> **Tip:** After connecting, access Jupyter at `http://localhost:8080` in your browser.

---

## 3. Clone the Repository (Deploy Key Setup)

The repository uses deploy keys for secure access. You'll create a key locally and configure it on both GitHub and the remote instance.

### Step A: Create the Deploy Key (Local Machine)

```bash
# Generate a new ED25519 SSH key
ssh-keygen -t ed25519 -C "GCP-Jupyter-Instance" -f ~/.ssh/ctf_agents_deploy_key

# Display the public key → Add this to GitHub Deploy Keys
cat ~/.ssh/ctf_agents_deploy_key.pub

# Display the private key → You'll copy this to the remote instance
cat ~/.ssh/ctf_agents_deploy_key
```

> **GitHub Setup:** Go to your repo → Settings → Deploy Keys → Add the public key.

### Step B: Configure the Deploy Key (Remote Instance)

After SSHing into the instance:

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Create the key file and paste your private key content
cat > ~/.ssh/ctf_agents_deploy_key << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
EOF

# Set correct permissions (required for SSH to use the key)
chmod 600 ~/.ssh/ctf_agents_deploy_key

# Add SSH config for GitHub with custom host alias
cat >> ~/.ssh/config << 'EOF'
Host github.com-ctf-agents
    HostName github.com
    User git
    IdentityFile ~/.ssh/ctf_agents_deploy_key
    IdentitiesOnly yes
EOF

chmod 600 ~/.ssh/config
```

### Step C: Clone the Repository

```bash
# Clone using the custom host alias
git clone git@github.com-ctf-agents:TATAR-LAB/ctf-agents.git
```

---

## 4. Environment Setup

Install dependencies and build the Docker environment.

### Install uv (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Install Python Dependencies

```bash
cd ctf-agents
uv venv
uv pip install -r requirements.txt
```

### Build Docker Image

```bash
cd docker/multiagent

# For Linux (GCP instances)
docker build -f Dockerfile -t ctfenv:multiagent .

# For Mac ARM (local development)
# docker build -f Dockerfile.arm -t ctfenv:multiagent .

# Create the Docker network for container communication
docker network create ctfnet

cd ../..
```

### Configure API Keys

```bash
# Create keys.cfg with your API keys
echo "OLLAMA=ollama" > keys.cfg

# Add other keys as needed, e.g.:
# echo "OPENAI_API_KEY=sk-..." >> keys.cfg
```

---

## Quick Reference

| Task                     | Command                                                                |
| ------------------------ | ---------------------------------------------------------------------- |
| Re-login (expired token) | `gcloud auth login --login-config=gcloud.json`                         |
| SSH to instance          | `gcloud compute ssh --zone "us-central1-a" "instance-20260112-153532"` |
| SSH with Jupyter port    | Add `-- -L 8080:localhost:8080` to SSH command                         |
| Check Docker containers  | `docker ps`                                                            |
