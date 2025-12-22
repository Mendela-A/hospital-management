# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port (якщо web-сервер слухає)
EXPOSE 8000

# Start the app
CMD ["python", "run.py"]
