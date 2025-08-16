# MetaTrader 5 Container (Wine)

This container bakes a recent MetaTrader 5 (MT5) build during image build and runs MT5 in portable mode with persistent volumes so updates survive restarts.

## Build

```bash
docker build -t mt5:latest -f infra/mt5/Dockerfile .
```

Or with Compose:

```bash
docker compose -f docker-compose.mt5.yml build
```

## Run (Apple Silicon friendly)

```bash
docker compose -f docker-compose.mt5.yml up -d
```

Notes:
- On Apple Silicon, this service enforces `platform: linux/amd64` to run under emulation.
- Volumes persist installation (`/opt/mt5`), data (`/opt/mt5_data`), and the Wine prefix (`/data/wine`).

## Verify

- Check logs to confirm MT5 started and remains healthy:
  ```bash
  docker compose -f docker-compose.mt5.yml logs -f mt5
  ```
- Verify the process is running in the container:
  ```bash
  docker exec -it $(docker compose -f docker-compose.mt5.yml ps -q mt5) bash -lc "pgrep -fa 'terminal(64)?\.exe'"
  ```

## Updates

- The image bakes a recent installer. MT5 may still self-update at runtime. Because install/data are stored in volumes, updates persist across restarts.
- To rebake to the newest MT5 build, rebuild the image:
  ```bash
  docker compose -f docker-compose.mt5.yml build --no-cache
  docker compose -f docker-compose.mt5.yml up -d --force-recreate
  ```

## Troubleshooting

- If MT5 fails to start, ensure volumes are writable and the host has sufficient memory/CPU.
- Time sync matters. On macOS, ensure system clock is correct. Inside container, you can set `TZ` env if needed.
- If the install volume is empty on first boot, it will be hydrated from the baked copy.