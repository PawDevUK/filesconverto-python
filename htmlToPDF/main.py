"""
HTML to PDF Converter - Main Application

This script downloads HTML from a URL and converts it to PDF format.
Uses only Python standard library modules.

Usage:
    python main.py <url> [output_file]
    
Examples:
    python main.py https://example.com
    python main.py https://example.com output.pdf
"""

import sys
from pathlib import Path
from typing import Optional

from html_downloader import download_html
from html_to_pdf import convert_html_to_pdf


def convert_url_to_pdf(url: str, output_path: Optional[Path] = None) -> bool:
    """
    Download HTML from URL and convert to PDF.
    
    Args:
        url: URL to download HTML from
        output_path: Optional path for output PDF file
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("HTML TO PDF CONVERTER")
    print("=" * 60)
    print(f"URL: {url}")
    
    # Generate output filename from URL if not provided
    if output_path is None:
        # Extract domain/path for filename
        url_clean = url.replace('https://', '').replace('http://', '')
        url_clean = url_clean.replace('/', '_').replace('?', '_').replace('&', '_')
        url_clean = url_clean[:50]  # Limit length
        output_path = Path(f"{url_clean}.pdf")
    
    print(f"Output: {output_path}")
    print("-" * 60)
    
    # Step 1: Download HTML
    print("\n[1/2] Downloading HTML content...")
    html_content, error = download_html(url)
    
    if error:
        print(f"  [ERROR] {error}")
        return False
    
    print(f"  [SUCCESS] Downloaded {len(html_content)} characters")
    
    # Step 2: Convert to PDF
    print("\n[2/2] Converting HTML to PDF...")
    success, error = convert_html_to_pdf(html_content, output_path)
    
    if error:
        print(f"  [ERROR] {error}")
        return False
    
    print(f"  [SUCCESS] PDF created: {output_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Input URL: {url}")
    print(f"Output PDF: {output_path}")
    
    if output_path.exists():
        file_size = output_path.stat().st_size
        print(f"File size: {file_size} bytes")
    
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <url> [output_file]")
        print()
        print("Examples:")
        print("  python main.py https://example.com")
        print("  python main.py https://example.com output.pdf")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    success = convert_url_to_pdf(url, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
