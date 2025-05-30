# Use a minimal Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy the MCP server script
COPY mcp_hello.py .

# Expose port 8080
EXPOSE 8080

# Set the entrypoint
CMD ["python", "mcp_hello.py"]
