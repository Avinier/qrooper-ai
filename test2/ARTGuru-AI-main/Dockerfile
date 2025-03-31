# Base node image
FROM node:20.15.0-alpine as base

# Set working directory
WORKDIR /app

# Install dependencies only when needed
FROM base as deps
COPY package.json package-lock.json ./
RUN npm ci

# Development image
FROM base as development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
