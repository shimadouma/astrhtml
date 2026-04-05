FROM ubuntu:24.04

ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update && apt-get install -y \
    ca-certificates \
    build-essential \
    curl \
    wget \
    git \
    gh \
    vim \
    sudo \
    openssh-client \
    gnupg \
    jq \
    ripgrep \
    fd-find \
    tree \
    less \
    file \
    unzip \
    zip \
    htop \
    strace \
    lsof \
    iproute2 \
    dnsutils \
    net-tools \
    locales \
    python3 \
    python3-pip \
    python3-venv \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/ \
    && mv /root/.local/bin/uvx /usr/local/bin/

# Install Node.js (required for Claude Code)
ARG NODE_MAJOR=22
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Adjust UID/GID of the ubuntu user to match the host user
RUN if [ "$USER_UID" != "1000" ]; then \
        groupmod --gid $USER_GID $USERNAME \
        && usermod --uid $USER_UID --gid $USER_GID $USERNAME \
        && chown -R $USER_UID:$USER_GID /home/$USERNAME; \
    fi

# Add user to sudoers
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Install Rust toolchain (system-wide via CARGO_HOME/RUSTUP_HOME)
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH="/usr/local/cargo/bin:${PATH}"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path \
    && chmod -R a+r /usr/local/rustup /usr/local/cargo \
    && find /usr/local/cargo/bin -type f -exec chmod a+x {} +

# Install Playwright system dependencies for headless Chromium
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libxshmfence1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code


# Generate post-start initialization script
RUN { \
      echo '#!/usr/bin/env bash'; \
      echo 'set -euo pipefail'; \
      echo ''; \
      echo '# Copy Claude OAuth credentials from read-only mount'; \
      echo 'if [ -f /host-claude/.credentials.json ]; then'; \
      echo '  mkdir -p "$HOME/.claude"'; \
      echo '  cp /host-claude/.credentials.json "$HOME/.claude/.credentials.json"'; \
      echo '  chmod 600 "$HOME/.claude/.credentials.json"'; \
      echo 'fi'; \
      echo 'if [ -f /host-claude.json ]; then'; \
      echo '  cp /host-claude.json "$HOME/.claude.json"'; \
      echo 'fi'; \
    } > /usr/local/bin/devcontainer-post-start.sh \
    && chmod +x /usr/local/bin/devcontainer-post-start.sh

USER ${USERNAME}
WORKDIR /home/${USERNAME}
