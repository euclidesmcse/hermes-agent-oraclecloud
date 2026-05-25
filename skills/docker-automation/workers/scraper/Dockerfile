FROM node:20-alpine

# Install puppeteer dependencies
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

WORKDIR /app

# Install dependencies
COPY package.json .
RUN npm install --production

# Copy worker code
COPY worker.js .

# Default command
CMD ["node", "/app/worker.js"]
