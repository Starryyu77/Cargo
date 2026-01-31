# --- Stage 1: Build Frontend ---
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ .

# Build the frontend (outputs to /app/frontend/dist)
RUN npm run build

# --- Stage 2: Setup Backend ---
FROM python:3.10-slim

WORKDIR /app

# Copy backend requirements
COPY requirements.txt .

# Install backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY MVP ./MVP

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Run the server
# Use sh to allow variable expansion if needed, though direct exec is preferred for signal handling.
# We hardcode port 8000 to match EXPOSE, but Render provides PORT env var.
# We will use the shell form to allow $PORT usage if passed by Render.
CMD uvicorn MVP.server:app --host 0.0.0.0 --port ${PORT:-8000}
