#!/usr/bin/env python3
"""
MCP Service for extracting specific pages from a PDF file.
"""

from pathlib import Path

from mcp.server import MCPServer
from pypdf import PdfReader, PdfWriter


server = MCPServer(name="pdf-extract", version="1.0.0")


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


@server.tool(description="Extract specific pages from a PDF file and save to a new PDF")
def extract_pages(input_path: str, output_path: str, pages: list[int] | str) -> str:
    """
    Extract specific pages from a PDF file and save to a new PDF.

    Args:
        input_path: Path to the input PDF file
        output_path: Path where the output PDF will be saved
        pages: Pages to extract - either a list of page numbers (1-based) or a range string,
               e.g. '1-10' for pages 1 to 10, '1-5,8,10-12' for multiple ranges
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    # Validate input file exists
    if not input_file.exists():
        return f"Error: Input file not found: {input_file}"

    # Validate file is PDF
    if not input_file.suffix.lower() == ".pdf":
        return f"Error: Input file must be a PDF: {input_file}"

    try:
        # Read input PDF
        reader = PdfReader(str(input_file))
        total_pages = len(reader.pages)

        # Parse pages input (supports both list and range string)
        page_numbers = parse_pages(pages, total_pages)

        # Validate page numbers
        invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
        if invalid_pages:
            return f"Error: Invalid page numbers {invalid_pages}. PDF has {total_pages} pages (valid range: 1-{total_pages})"

        # Create output PDF with selected pages
        writer = PdfWriter()
        for page_num in page_numbers:
            writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based indexing

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write output PDF
        with open(output_file, "wb") as f:
            writer.write(f)

        return f"Successfully extracted {len(page_numbers)} pages to {output_file}"

    except Exception as e:
        return f"Error: {str(e)}"


def main():
    server.run()


if __name__ == "__main__":
    main()
