#!/usr/bin/env bash
set -euo pipefail

: "${WINEPREFIX:=/data/wine}"
: "${WINEARCH:=win64}"
: "${DISPLAY:=:99}"
: "${MT5_INSTALL_DIR:=/opt/mt5}"
: "${MT5_DATA_DIR:=/opt/mt5_data}"

# Start Xvfb if not already running
if ! pgrep -f "Xvfb ${DISPLAY}" >/dev/null 2>&1; then
	rm -f /tmp/.X99-lock || true
	Xvfb "${DISPLAY}" -screen 0 1280x800x24 -ac +extension GLX +render -noreset &
fi

sleep 1

# Hydrate install volume on first run
if [ -z "$(ls -A "${MT5_INSTALL_DIR}" 2>/dev/null)" ] && [ -d /opt/mt5_baked ]; then
	cp -a /opt/mt5_baked/. "${MT5_INSTALL_DIR}/"
fi

# Determine executable path
EXE=""
if [ -f "${MT5_INSTALL_DIR}/terminal64.exe" ]; then
	EXE="${MT5_INSTALL_DIR}/terminal64.exe"
elif [ -f "${MT5_INSTALL_DIR}/terminal.exe" ]; then
	EXE="${MT5_INSTALL_DIR}/terminal.exe"
else
	if [ -f "${WINEPREFIX}/drive_c/Program Files/MetaTrader 5/terminal64.exe" ]; then
		EXE="${WINEPREFIX}/drive_c/Program Files/MetaTrader 5/terminal64.exe"
	elif [ -f "${WINEPREFIX}/drive_c/Program Files/MetaTrader 5 Trading Platform/terminal64.exe" ]; then
		EXE="${WINEPREFIX}/drive_c/Program Files/MetaTrader 5 Trading Platform/terminal64.exe"
	fi
fi

if [ -z "${EXE}" ]; then
	echo "[entrypoint] MT5 executable not found" >&2
	exec sleep infinity
fi

mkdir -p "${MT5_DATA_DIR}"

echo "[entrypoint] Starting MetaTrader 5 with WINEPREFIX=${WINEPREFIX}"
exec xvfb-run -a wine "${EXE}" /portable