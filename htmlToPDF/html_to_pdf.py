"""
HTML to PDF Converter Module

This module provides functionality to convert HTML content to PDF format.
Uses only Python standard library modules.

The converter parses HTML content and generates a basic PDF with:
- Text content extraction
- Basic formatting preservation
- Simple layout generation
"""

import re
import zlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from html.parser import HTMLParser
from datetime import datetime


class HTMLContentParser(HTMLParser):
    """Parser to extract text content and basic structure from HTML."""
    
    def __init__(self):
        super().__init__()
        self.content: List[Dict] = []
        self.current_text = ""
        self.current_style = {
            'bold': False,
            'italic': False,
            'heading': 0,
            'list_item': False
        }
        self.in_body = False
        self.skip_tags = {'script', 'style', 'head', 'meta', 'link', 'noscript'}
        self.skip_depth = 0
        
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag = tag.lower()
        
        if tag in self.skip_tags:
            self.skip_depth += 1
            return
            
        if tag == 'body':
            self.in_body = True
            
        if tag in ('b', 'strong'):
            self._flush_text()
            self.current_style['bold'] = True
        elif tag in ('i', 'em'):
            self._flush_text()
            self.current_style['italic'] = True
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._flush_text()
            self.current_style['heading'] = int(tag[1])
        elif tag in ('p', 'div', 'br', 'hr'):
            self._flush_text()
        elif tag == 'li':
            self._flush_text()
            self.current_style['list_item'] = True
            
    def handle_endtag(self, tag: str):
        tag = tag.lower()
        
        if tag in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
            
        if tag in ('b', 'strong'):
            self._flush_text()
            self.current_style['bold'] = False
        elif tag in ('i', 'em'):
            self._flush_text()
            self.current_style['italic'] = False
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._flush_text()
            self.current_style['heading'] = 0
        elif tag in ('p', 'div'):
            self._flush_text()
        elif tag == 'li':
            self._flush_text()
            self.current_style['list_item'] = False
            
    def handle_data(self, data: str):
        if self.skip_depth > 0:
            return
        self.current_text += data
        
    def _flush_text(self):
        text = self.current_text.strip()
        if text:
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            self.content.append({
                'text': text,
                'bold': self.current_style['bold'],
                'italic': self.current_style['italic'],
                'heading': self.current_style['heading'],
                'list_item': self.current_style['list_item']
            })
        self.current_text = ""
        
    def get_content(self) -> List[Dict]:
        self._flush_text()
        return self.content


def parse_html(html_content: str) -> List[Dict]:
    """
    Parse HTML content and extract text with basic formatting.
    
    Args:
        html_content: HTML string to parse
        
    Returns:
        List of dictionaries containing text and formatting information
    """
    parser = HTMLContentParser()
    parser.feed(html_content)
    return parser.get_content()


def _escape_pdf_string(text: str) -> str:
    """Escape special characters for PDF string."""
    # Escape backslash first, then parentheses
    text = text.replace('\\', '\\\\')
    text = text.replace('(', '\\(')
    text = text.replace(')', '\\)')
    return text


def _create_pdf_content_stream(content: List[Dict], page_width: float, page_height: float) -> bytes:
    """
    Create PDF content stream from parsed HTML content.
    
    Args:
        content: Parsed HTML content
        page_width: Page width in points
        page_height: Page height in points
        
    Returns:
        PDF content stream as bytes
    """
    stream_parts = []
    y_position = page_height - 72  # Start 1 inch from top
    margin_left = 72  # 1 inch left margin
    line_height = 14
    max_chars_per_line = 80
    
    stream_parts.append("BT\n")  # Begin text
    
    for item in content:
        text = item['text']
        heading = item.get('heading', 0)
        is_list_item = item.get('list_item', False)
        
        # Set font based on style
        if heading > 0:
            font_size = max(24 - (heading - 1) * 2, 12)
            stream_parts.append(f"/F1 {font_size} Tf\n")
            line_height = font_size + 4
        else:
            stream_parts.append("/F1 12 Tf\n")
            font_size = 12
            line_height = 14
        
        # Handle list items
        prefix = "• " if is_list_item else ""
        text = prefix + text
        
        # Word wrap the text
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) > max_chars_per_line:
                if current_line:
                    # Output current line
                    escaped_text = _escape_pdf_string(current_line)
                    stream_parts.append(f"{margin_left} {y_position} Td\n")
                    stream_parts.append(f"({escaped_text}) Tj\n")
                    y_position -= line_height
                    
                    # Check for page break
                    if y_position < 72:
                        stream_parts.append("ET\n")
                        return ''.join(stream_parts).encode('latin-1', errors='replace')
                    
                current_line = word
            else:
                current_line = test_line
        
        # Output remaining text
        if current_line:
            escaped_text = _escape_pdf_string(current_line)
            stream_parts.append(f"{margin_left} {y_position} Td\n")
            stream_parts.append(f"({escaped_text}) Tj\n")
            y_position -= line_height
            
            if y_position < 72:
                stream_parts.append("ET\n")
                return ''.join(stream_parts).encode('latin-1', errors='replace')
        
        # Add spacing after headings
        if heading > 0:
            y_position -= line_height // 2
    
    stream_parts.append("ET\n")  # End text
    return ''.join(stream_parts).encode('latin-1', errors='replace')


def convert_html_to_pdf(html_content: str, output_path: Path, 
                        page_width: float = 612, page_height: float = 792) -> Tuple[bool, Optional[str]]:
    """
    Convert HTML content to PDF.
    
    Args:
        html_content: HTML string to convert
        output_path: Path where the PDF should be saved
        page_width: Page width in points (default: Letter width 8.5")
        page_height: Page height in points (default: Letter height 11")
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Parse HTML content
        content = parse_html(html_content)
        
        if not content:
            return False, "No content could be extracted from HTML"
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF content stream
        content_stream = _create_pdf_content_stream(content, page_width, page_height)
        
        # Build PDF structure
        pdf_parts = []
        xref_positions = []
        
        # PDF Header
        pdf_parts.append(b'%PDF-1.4\n')
        pdf_parts.append(b'%\xe2\xe3\xcf\xd3\n')  # Binary marker
        
        # Object 1: Catalog
        xref_positions.append(sum(len(p) for p in pdf_parts))
        pdf_parts.append(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
        
        # Object 2: Pages
        xref_positions.append(sum(len(p) for p in pdf_parts))
        pdf_parts.append(b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n')
        
        # Object 3: Page
        xref_positions.append(sum(len(p) for p in pdf_parts))
        page_obj = f'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n'
        pdf_parts.append(page_obj.encode('latin-1'))
        
        # Object 4: Content stream
        xref_positions.append(sum(len(p) for p in pdf_parts))
        stream_length = len(content_stream)
        pdf_parts.append(f'4 0 obj\n<< /Length {stream_length} >>\nstream\n'.encode('latin-1'))
        pdf_parts.append(content_stream)
        pdf_parts.append(b'\nendstream\nendobj\n')
        
        # Object 5: Font
        xref_positions.append(sum(len(p) for p in pdf_parts))
        pdf_parts.append(b'5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n')
        
        # Cross-reference table
        xref_start = sum(len(p) for p in pdf_parts)
        xref_lines = [b'xref\n', b'0 6\n', b'0000000000 65535 f \n']
        for pos in xref_positions:
            xref_lines.append(f'{pos:010d} 00000 n \n'.encode('latin-1'))
        pdf_parts.extend(xref_lines)
        
        # Trailer
        pdf_parts.append(b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n')
        pdf_parts.append(f'{xref_start}\n'.encode('latin-1'))
        pdf_parts.append(b'%%EOF\n')
        
        # Write PDF to file
        with open(output_path, 'wb') as f:
            for part in pdf_parts:
                f.write(part)
        
        return True, None
        
    except Exception as e:
        return False, f"Error converting HTML to PDF: {str(e)}"
