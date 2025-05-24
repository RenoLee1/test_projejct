# Start from a Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install git and OpenSSH to use SSH for cloning
RUN apt-get update && apt-get install -y git openssh-client

# Install dependencies first to leverage Docker cache
COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

# Add src to PYTHONPATH
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy application code
COPY . .

# Expose API port
EXPOSE 8081

# Run FastAPI app with uvicorn
# To enable hot-reloading when modifying code, add reload parameter to dockerfile
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
