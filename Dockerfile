# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY MVP ./MVP

# Copy the frontend build artifacts
# Note: Ensure you run 'npm run build' locally before building this Docker image
# or set up a multi-stage build. For simplicity, we assume dist exists.
COPY frontend/dist ./frontend/dist

# Expose the port the app runs on
EXPOSE 8000

# Define environment variable
ENV PORT=8000

# Run uvicorn when the container launches
CMD ["uvicorn", "MVP.server:app", "--host", "0.0.0.0", "--port", "8000"]
