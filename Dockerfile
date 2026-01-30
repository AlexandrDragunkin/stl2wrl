# Dockerfile for testing stl2wrl with Python 3.7
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies
RUN pip install --no-cache-dir pytest

# Run tests
CMD ["pytest"]