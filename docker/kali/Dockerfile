# Kali Linux Docker Image for D-CIPHER CTF Solving
# Based on vxcontrol/kali-linux with additional CTF tools
FROM vxcontrol/kali-linux:latest

ENV DEBIAN_FRONTEND=noninteractive

# Update and install Kali meta-packages and additional tools
RUN apt-get update && apt-get install -y \
    # Core tools
    sudo curl wget git vim unzip jq file \
    build-essential pkg-config \
    # Python
    python3-dev python3-pip python3-venv \
    # Kali tools (many already included, but ensure they're present)
    nmap netcat-openbsd \
    sqlmap nikto gobuster dirb wfuzz \
    john hashcat hydra medusa \
    binwalk foremost steghide exiftool \
    gdb radare2 \
    # Forensics
    sleuthkit \ 
    # volatility3 \
    # Crypto
    openssl \
    # Java for Ghidra
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Ghidra
WORKDIR /tmp
RUN wget -q https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.1_build/ghidra_11.0.1_PUBLIC_20240130.zip && \
    unzip -q -d /opt/ghidra ghidra_11.0.1_PUBLIC_20240130.zip && \
    rm ghidra_11.0.1_PUBLIC_20240130.zip
RUN mkdir -p /opt/ghidra/customScripts/
COPY ghidra_scripts/DecompileToJson.java /opt/ghidra/customScripts/DecompileToJson.java
COPY ghidra_scripts/DisassembleToJson.java /opt/ghidra/customScripts/DisassembleToJson.java
COPY ghidra_scripts/decompile.sh /opt/ghidra/customScripts/decompile.sh
COPY ghidra_scripts/disassemble.sh /opt/ghidra/customScripts/disassemble.sh

# Install Python packages for CTF
RUN pip3 install --break-system-packages --upgrade pip && \
    pip3 install --break-system-packages pwntools gmpy2 angr chepy z3-solver

# Create a non-root user with sudo permissions
ARG HOST_UID=1000
ARG USERNAME=ctfplayer
ARG USER_UID=$HOST_UID
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME 2>/dev/null || true && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME 2>/dev/null || true && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to user
USER $USERNAME
WORKDIR /home/$USERNAME
RUN mkdir -p ctf_files

# Copy entrypoint script
COPY entrypoint.sh /home/$USERNAME/.entrypoint.sh

CMD ["bash", "/home/ctfplayer/.entrypoint.sh"]
