from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="hashnode-mcp-server",
    version="0.1.0",
    author="Hashnode MCP Server Contributors",
    author_email="mail@budhathokisagar.com.np",
    description="A Model Context Protocol server for interacting with the Hashnode API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sbmagar13/hashnode-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hashnode-mcp-server=hashnode_mcp.mcp_server:main",
        ],
    },
)
