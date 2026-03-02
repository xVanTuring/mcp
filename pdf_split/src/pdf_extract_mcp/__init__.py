#!/usr/bin/env python3
"""
MCP Service for extracting specific pages from a PDF file.
"""

import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from pypdf import PdfReader, PdfWriter


app = Server("pdf-extract")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="extract_pages",
            description="Extract specific pages from a PDF file and save to a new PDF",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the input PDF file",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the output PDF will be saved",
                    },
                    "pages": {
                        "oneOf": [
                            {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of page numbers to extract (1-based indexing)",
                            },
                            {
                                "type": "string",
                                "description": "Page range string, e.g., '1-10' for pages 1 to 10, '1-5,8,10-12' for multiple ranges",
                            },
                        ],
                        "description": "Pages to extract - either a list of integers or a range string",
                    },
                },
                "required": ["input_path", "output_path", "pages"],
            },
        )
    ]


def parse_pages(pages_input, total_pages):
    """Parse pages input (list or range string) into a sorted list of unique page numbers."""
    pages = set()

    if isinstance(pages_input, list):
        # Handle list of integers
        for p in pages_input:
            if isinstance(p, int):
                pages.add(p)
    elif isinstance(pages_input, str):
        # Handle range string like "1-10" or "1-5,8,10-12"
        parts = [p.strip() for p in pages_input.split(",")]
        for part in parts:
            if "-" in part:
                # Range like "1-10"
                try:
                    start, end = part.split("-")
                    start = int(start.strip())
                    end = int(end.strip())
                    if start <= end:
                        pages.update(range(start, end + 1))
                except ValueError:
                    continue
            else:
                # Single page
                try:
                    pages.add(int(part))
                except ValueError:
                    continue

    return sorted(list(pages))


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "extract_pages":
        raise ValueError(f"Unknown tool: {name}")

    input_path = Path(arguments["input_path"])
    output_path = Path(arguments["output_path"])
    pages_input = arguments["pages"]

    # Validate input file exists
    if not input_path.exists():
        return [
            TextContent(type="text", text=f"Error: Input file not found: {input_path}")
        ]

    # Validate file is PDF
    if not input_path.suffix.lower() == ".pdf":
        return [
            TextContent(
                type="text", text=f"Error: Input file must be a PDF: {input_path}"
            )
        ]

    try:
        # Read input PDF
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        # Parse pages input (supports both list and range string)
        pages = parse_pages(pages_input, total_pages)

        # Validate page numbers
        invalid_pages = [p for p in pages if p < 1 or p > total_pages]
        if invalid_pages:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Invalid page numbers {invalid_pages}. PDF has {total_pages} pages (valid range: 1-{total_pages})",
                )
            ]

        # Create output PDF with selected pages
        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based indexing

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write output PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return [
            TextContent(
                type="text",
                text=f"Successfully extracted {len(pages)} pages to {output_path}",
            )
        ]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def main():
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
