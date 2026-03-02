# PDF Extract MCP Service

A Model Context Protocol (MCP) service for extracting specific pages from PDF files.

## Installation

```bash
pip install -e .
```

## Usage

This MCP service provides a tool called `extract_pages` that extracts specific pages from a PDF file.

### Tool: extract_pages

**Parameters:**

- `input_path` (string): Path to the input PDF file
- `output_path` (string): Path where the output PDF will be saved
- `pages` (array of integers): List of page numbers to extract (1-based indexing)

### Example

```json
{
  "input_path": "/path/to/input.pdf",
  "output_path": "/path/to/output.pdf",
  "pages": [1, 3, 5]
}
```

## Running the Service

```bash
python pdf_extract_mcp.py
```

Or after installation:

```bash
pdf-extract-mcp
```

## Claude Desktop Configuration

Add this to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "pdf-extract": {
      "command": [
        "uvx",
        "--from",
        "git+https://github.com/xVanTuring/mcp.git#subdirectory=pdf_split",
        "pdf-extract-mcp"
      ]
    }
  }
}
```
