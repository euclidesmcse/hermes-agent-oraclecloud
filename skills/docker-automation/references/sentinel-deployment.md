# Updated Docker deployment of SENTINEL

This document captures the latest recommended approach for containerizing SENTINEL as of 2026-05-26.

## Recommended deployment pattern

1. **Expose Sentinel port directly** – Sentinel already listens on port 5000 inside the container. You can map host port 5000 directly:

   ```bash
   docker run -d \
     --name sentinel \
     -v $HOME/hermescompany:/app \
     -p 5000:5000 \
     sentinel-app
   ```

   No `--privileged` or `--cap-add=SYS_ADMIN` is required if you only need the HTTP API endpoint.

2. **Optional: lightweight tasks‑web container** (if you want a separate HTTP server for `/tasks/`)

   ```bash
   docker run -d \
     --name tasks-web \
     -v $HOME/hermescompany:/app \
     -p 5001:5000 \
     python:3.9-slim \
     python -m http.server 5000 --bind 0.0.0.0
   ```

   Then configure Nginx:

   ```nginx
   location /tasks/ {
       proxy_pass http://127.0.0.1:5001;
   }
   ```

3. **Verification** – after starting the container(s), check:

   ```bash
   docker logs sentinel
   curl -I http://137.131.167.198/agenda/
   curl -I http://137.131.167.198/tasks/
   ```

   Both should return `HTTP/1.1 200 OK`.

4. **References** – see the original `docker-deploy-sentinel` skill for additional pitfalls and verification steps.

For more details, see `references/docker-deploy-sentinel-setup.md`.