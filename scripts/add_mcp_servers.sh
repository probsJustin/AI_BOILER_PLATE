#!/bin/bash

# Script to add MCP server configurations to Claude Code
# This script configures the GeoJSON, Gitea, and Notes MCP servers

echo "Adding MCP server configurations to Claude Code..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define the MCP configuration files
GEOJSON_CONFIG="$PROJECT_ROOT/mcp/geoJson/geojson_claude_mcp.json"
GITEA_CONFIG="$PROJECT_ROOT/mcp/git/gitea_claude_mcp.json"
NOTES_CONFIG="$PROJECT_ROOT/mcp/notes/notes_claude_mcp.json"

# Check if claude command is available
if ! command -v claude &> /dev/null; then
    echo "Error: 'claude' command not found. Please ensure Claude Code is installed and in your PATH."
    exit 1
fi

# Function to add MCP server
add_mcp_server() {
    local server_url="$1"
    local server_name="$2"
    
    echo "Adding $server_name server..."
    
    # Add MCP server using claude command with HTTP URL and SSE transport
    claude mcp add -t sse "$server_name" "$server_url"
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully added $server_name server"
    else
        echo "✗ Failed to add $server_name server"
        return 1
    fi
}

# Add each MCP server
echo "Starting MCP server configuration..."
echo

# Add GeoJSON MCP Server
add_mcp_server "http://localhost:8000" "GeoJSON MCP Server"
echo

# Add Gitea MCP Server
add_mcp_server "http://localhost:3000" "Gitea MCP Server"
echo

# Add Notes MCP Server
add_mcp_server "http://localhost:8002" "Markdown Git Notes MCP Server"
echo

echo "MCP server configuration complete!"
echo
echo "To verify the configurations, you can run:"
echo "  claude mcp list"
echo

# Function to start Docker containers
start_docker_containers() {
    echo "Starting Docker containers..."
    echo
    
    # Start GeoJSON MCP Server
    echo "Starting GeoJSON MCP Server..."
    cd "$PROJECT_ROOT/mcp/geoJson" && docker-compose up -d
    if [ $? -eq 0 ]; then
        echo "✓ GeoJSON MCP Server started successfully"
    else
        echo "✗ Failed to start GeoJSON MCP Server"
    fi
    echo
    
    # Start Gitea MCP Server
    echo "Starting Gitea MCP Server..."
    cd "$PROJECT_ROOT/mcp/git" && docker-compose up -d
    if [ $? -eq 0 ]; then
        echo "✓ Gitea MCP Server started successfully"
    else
        echo "✗ Failed to start Gitea MCP Server"
    fi
    echo
    
    # Start Notes MCP Server
    echo "Starting Markdown Git Notes MCP Server..."
    cd "$PROJECT_ROOT/mcp/notes" && docker-compose up -d
    if [ $? -eq 0 ]; then
        echo "✓ Markdown Git Notes MCP Server started successfully"
    else
        echo "✗ Failed to start Markdown Git Notes MCP Server"
    fi
    echo
    
    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Check if docker and docker-compose are available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Docker and docker-compose detected. Starting MCP servers..."
    echo
    start_docker_containers
    
    echo "To check the status of the containers, run:"
    echo "  docker ps"
    echo
    echo "To view logs for a specific server, run:"
    echo "  docker-compose -f $PROJECT_ROOT/mcp/geoJson/docker-compose.yaml logs"
    echo "  docker-compose -f $PROJECT_ROOT/mcp/git/docker-compose.yaml logs"
    echo "  docker-compose -f $PROJECT_ROOT/mcp/notes/docker-compose.yaml logs"
else
    echo "Docker or docker-compose not found. Please install them to run the MCP servers."
    echo
    echo "To start the MCP servers manually after installing Docker, run:"
    echo "  cd $PROJECT_ROOT/mcp/geoJson && docker-compose up -d"
    echo "  cd $PROJECT_ROOT/mcp/git && docker-compose up -d"
    echo "  cd $PROJECT_ROOT/mcp/notes && docker-compose up -d"
fi

# Output Windows path docker commands
echo
echo "================================"
echo "Windows Path Docker Commands:"
echo "================================"
# Convert WSL path to Windows path
WINDOWS_PATH=$(echo "$PROJECT_ROOT" | sed 's|/mnt/c/|C:\\|' | sed 's|/|\\|g')
echo
echo "To start the MCP servers from Windows (PowerShell or Command Prompt):"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\geoJson\\docker-compose.yaml\" up -d"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\git\\docker-compose.yaml\" up -d"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\notes\\docker-compose.yaml\" up -d"
echo
echo "To check logs from Windows:"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\geoJson\\docker-compose.yaml\" logs"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\git\\docker-compose.yaml\" logs"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\notes\\docker-compose.yaml\" logs"
echo
echo "To stop the servers from Windows:"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\geoJson\\docker-compose.yaml\" down"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\git\\docker-compose.yaml\" down"
echo "  docker-compose -f \"$WINDOWS_PATH\\mcp\\notes\\docker-compose.yaml\" down"