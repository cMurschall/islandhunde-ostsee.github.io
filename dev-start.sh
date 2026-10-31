#!/bin/bash

# Definitionen für den Container
IMAGE="hugomods/hugo:debian-dart-sass-node-git-non-root-0.147.9"
PROJECT_DIR="/src"
HOST_PORT="1313"

# Funktion für Schritte, die KEINE Root-Rechte benötigen (Hugo, npm)
run_as_user() {
  local command_to_run="$1"
  echo ">>> Running command as user: ${command_to_run}"
  docker run --rm -it \
    -v "${PWD}:${PROJECT_DIR}" \
    --user "$(id -u):$(id -g)" \
    "${IMAGE}" \
    sh -c "${command_to_run}"
}

# Funktion für Schritte, die Root-Rechte benötigen (apt-get)
run_as_root() {
  local command_to_run="$1"
  echo ">>> Running command as root: ${command_to_run}"
  docker run --rm -it \
    -v "${PWD}:${PROJECT_DIR}" \
    --user "root" \
    "${IMAGE}" \
    sh -c "${command_to_run}"
}


# --- Schritte aus der GitHub Action ---
echo "Starting development environment setup..."

echo "0. Cleaning up previous build directory (public/)..."
run_as_root "rm -rf ${PROJECT_DIR}/public"

echo "0.5. Cleaning up Hugo cache (resources/)..."
run_as_root "rm -rf ${PROJECT_DIR}/resources"

echo "1. Installing Node.js dependencies (npm install)..."
run_as_user "npm install"

echo "2. Cleaning Hugo cache (hugo --gc)..."
run_as_user "hugo --gc"

# NEU: Root-Berechtigungen mit SUDO erzwingen
echo "3. Installing Python/Pip/Pillow (REQUIRES ROOT) and converting images..."
# Führt rm -rf /var/lib/apt/lists/* als Root aus und startet dann die APT-Installation.
run_as_root "rm -rf /var/lib/apt/lists/* && apt-get update -y --allow-releaseinfo-change && apt-get install -y python3 python3-pil && python3 scripts/convert-to-webp.py"


# Startet den Hugo-Entwicklungsserver mit Live-Reload und korrekter baseURL
docker run --rm -it \
  -v "${PWD}:${PROJECT_DIR}" \
  -p "${HOST_PORT}:${HOST_PORT}" \
  --user "root" \
  "${IMAGE}" \
  sh -c "
    echo '>>> Installing Python...' &&
    apt-get update -y --allow-releaseinfo-change > /dev/null &&
    apt-get install -y python3 > /dev/null &&
    echo '>>> Starting Hugo development server on http://localhost:${HOST_PORT}...' &&
    hugo server --bind 0.0.0.0 -D --baseURL '/'
  "


