#!/usr/bin/env bash
SUDO=""
if command -v sudo &> /dev/null; then
    SUDO="sudo"
fi

if command -v apt &> /dev/null; then
    $SUDO apt update && $SUDO apt install -y git-lfs jq \
        libpixman-1-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libjpeg-dev \
        libgif-dev \
        librsvg2-dev
elif command -v brew &> /dev/null; then
    brew install git-lfs jq
elif command -v dnf &> /dev/null; then
    $SUDO dnf install -y git-lfs jq
else
    echo "Error: Could not find package manager to install git-lfs and jq"
    exit 1
fi
