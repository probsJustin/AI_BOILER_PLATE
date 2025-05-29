# Use a minimal Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /app

# Copy the MCP server code
COPY mcp_server.py .

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Expose the app port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
