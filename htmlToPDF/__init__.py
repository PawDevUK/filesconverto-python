"""
HTML to PDF Converter Package

This package provides functionality to download HTML content from URLs
and convert it to PDF format using only Python standard library modules.

Modules:
    html_downloader: Download HTML content from URLs
    html_to_pdf: Convert HTML content to PDF format
    main: Command-line interface for the converter
"""

from .html_downloader import download_html, save_html_to_file, download_html_to_file
from .html_to_pdf import parse_html, convert_html_to_pdf

__all__ = [
    'download_html',
    'save_html_to_file',
    'download_html_to_file',
    'parse_html',
    'convert_html_to_pdf',
]
