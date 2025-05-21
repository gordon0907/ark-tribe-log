FROM python:3
LABEL authors="Gordon"

# Set working directory inside container
WORKDIR /usr/src/app

# Copy dependency list and application script
COPY requirements.txt .
COPY server.py .

# Install Python dependencies
RUN pip install --no-cache-dir --requirement requirements.txt

# Declare a mount point for external data
VOLUME ["/SavedArks"]

# Expose port 80 for HTTP
EXPOSE 80/tcp

# Default command to run the app
CMD ["python", "server.py"]
