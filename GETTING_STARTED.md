# Getting Started with Hashnode MCP Server

This guide will help you get started with the Hashnode MCP Server.

## Prerequisites

- Python 3.8 or higher
- A Hashnode account with a personal access token

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sbmagar13/hashnode-mcp-server.git
   cd hashnode-mcp-server
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   Alternatively, you can use the Makefile:
   ```bash
   make setup
   ```

## Configuration

1. Create a `.env` file in the root directory based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Hashnode personal access token:
   ```
   HASHNODE_PERSONAL_ACCESS_TOKEN=your_personal_access_token_here
   ```

   You can get your personal access token from your Hashnode account settings.

## Running the Server

1. Run the server:
   ```bash
   python run_server.py
   ```

   Alternatively, you can use the Makefile:
   ```bash
   make run
   ```

2. The server uses **stdio transport** by default, which is the standard for MCP servers. It communicates via stdin/stdout with the MCP client (e.g., Claude Desktop, Cline).

## Using the Server

Once the server is running, you can use it with any MCP client. The server exposes tools for creating, updating, deleting, and searching articles, managing webhooks, and more. See the [README.md](README.md) file for the full list of available tools.

## Running Tests

Run the tests to ensure everything is working correctly:
```bash
pytest
```

Alternatively, you can use the Makefile:
```bash
make test
```

## Next Steps

- Read the [README.md](README.md) file for more information about the project.
- Explore the [API documentation](README.md#available-tools) to learn about the available tools.
- Contribute to the project by following the [contributing guidelines](CONTRIBUTING.md).
