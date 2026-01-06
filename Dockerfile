# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose any necessary ports (if bot listens on a port, but usually not for Telegram)
# EXPOSE 8080  # Uncomment if needed

# Run the bot
CMD ["python", "bot.py"]