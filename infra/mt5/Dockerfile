# syntax=docker/dockerfile:1
ARG DEBIAN_FRONTEND=noninteractive
FROM debian:bookworm-slim

RUN dpkg --add-architecture i386 \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		wine64 wine32 winbind xvfb cabextract wget unzip ca-certificates tzdata xauth procps \
	&& rm -rf /var/lib/apt/lists/*

ENV WINEARCH=win64
ENV WINEPREFIX=/data/wine
ENV DISPLAY=:99
ENV MT5_INSTALL_DIR=/opt/mt5
ENV MT5_DATA_DIR=/opt/mt5_data

RUN mkdir -p "$MT5_INSTALL_DIR" "$MT5_DATA_DIR" "$WINEPREFIX"

COPY install_mt5.sh /usr/local/bin/install_mt5.sh
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/install_mt5.sh /usr/local/bin/entrypoint.sh \
	&& /usr/local/bin/install_mt5.sh

# Seed a baked copy to rehydrate runtime volumes on first start
RUN mkdir -p /opt/mt5_baked \
	&& if [ -d "$WINEPREFIX/drive_c/Program Files/MetaTrader 5" ]; then \
		cp -a "$WINEPREFIX/drive_c/Program Files/MetaTrader 5/." /opt/mt5_baked/; \
	elif [ -d "$WINEPREFIX/drive_c/Program Files/MetaTrader 5 Trading Platform" ]; then \
		cp -a "$WINEPREFIX/drive_c/Program Files/MetaTrader 5 Trading Platform/." /opt/mt5_baked/; \
	fi

VOLUME ["/opt/mt5", "/opt/mt5_data", "/data/wine"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s CMD pgrep -fa 'terminal(64)?\\.exe' >/dev/null || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]