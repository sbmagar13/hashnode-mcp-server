#!/usr/bin/env python
"""
Script to run the Hashnode MCP server.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

# Import the main function from the package
from hashnode_mcp.mcp_server import main

if __name__ == "__main__":
    print("Starting Hashnode MCP server...")
    main()
