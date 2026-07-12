#!/usr/bin/env python
"""
Hashnode MCP Server - Root entry point.

This file is a thin shim for backwards compatibility with users who
reference mcp_server.py directly. All logic lives in hashnode_mcp/mcp_server.py.
"""
from hashnode_mcp.mcp_server import main, mcp  # noqa: F401

if __name__ == "__main__":
    main()
