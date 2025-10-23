# Multi-stage build for FHU FRANKO application
FROM node:20-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ ./

# Build arguments from Railway
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_ADMIN_PATH

# Set environment variables for build
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV REACT_APP_ADMIN_PATH=${REACT_APP_ADMIN_PATH}
ENV NODE_ENV=production

# Install dependencies and build
RUN yarn install
RUN yarn build

# Python backend stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create uploads directory
RUN mkdir -p /app/backend/uploads/buses

# Expose port
EXPOSE 8001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8001
ENV PYTHONPATH=/app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/ || exit 1

# Start command - Railway will set PORT
WORKDIR /app/backend
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
