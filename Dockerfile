# Use the exact Python version you want
FROM python:3.10.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files (main.py etc.)
COPY . .

# Command to run your bot
CMD ["python", "main.py"]
