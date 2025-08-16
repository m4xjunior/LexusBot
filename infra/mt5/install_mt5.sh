#!/usr/bin/env bash
set -euo pipefail

: "${WINEPREFIX:=/data/wine}"
: "${WINEARCH:=win64}"

mkdir -p "$WINEPREFIX"

# Initialize Wine prefix (may fail harmlessly during build)
wineboot -u || true

TMP_DIR=/tmp/mt5
mkdir -p "$TMP_DIR"
cd "$TMP_DIR"

MT5_URLS=(
	"https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
	"https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/MetaTrader5Setup.exe"
)

rm -f mt5setup.exe || true
for url in "${MT5_URLS[@]}"; do
	if wget -q -O mt5setup.exe "$url"; then
		break
	fi
	done

if [ ! -s mt5setup.exe ]; then
	echo "[install_mt5] Failed to download MT5 setup" >&2
	exit 1
fi

# Try silent install variants under Xvfb
set +e
xvfb-run -a wine mt5setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR="C:\\Program Files\\MetaTrader 5"
STATUS=$?
if [ $STATUS -ne 0 ]; then
	xvfb-run -a wine mt5setup.exe /silent
	STATUS=$?
fi
if [ $STATUS -ne 0 ]; then
	xvfb-run -a wine mt5setup.exe
	STATUS=$?
fi
set -e

sleep 5

if [ ! -d "$WINEPREFIX/drive_c/Program Files/MetaTrader 5" ] && [ ! -d "$WINEPREFIX/drive_c/Program Files/MetaTrader 5 Trading Platform" ]; then
	echo "[install_mt5] MT5 installation folder not found" >&2
	exit 1
fi

echo "[install_mt5] MT5 installation completed"