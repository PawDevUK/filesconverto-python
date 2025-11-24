"""
HTML Downloader Module

This module provides functionality to download HTML content from URLs.
The downloaded HTML can be saved to disk or returned as a string for further processing.
"""

import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple


def download_html(url: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """
    Download HTML content from a URL.
    
    Args:
        url: The URL to download HTML from
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (html_content, error_message)
        If successful, html_content contains the HTML string and error_message is None.
        If failed, html_content is None and error_message contains the error description.
    """
    try:
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            # Read the content
            content = response.read()
            
            # Try to determine encoding from headers
            charset = response.headers.get_content_charset()
            if charset:
                html_content = content.decode(charset)
            else:
                # Try common encodings
                for encoding in ['utf-8', 'latin-1', 'ascii']:
                    try:
                        html_content = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # Fallback to utf-8 with error handling
                    html_content = content.decode('utf-8', errors='replace')
            
            return html_content, None
            
    except urllib.error.HTTPError as e:
        return None, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return None, f"URL Error: {e.reason}"
    except TimeoutError:
        return None, f"Timeout after {timeout} seconds"
    except Exception as e:
        return None, f"Error downloading HTML: {str(e)}"


def save_html_to_file(html_content: str, output_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Save HTML content to a file.
    
    Args:
        html_content: The HTML string to save
        output_path: Path where the file should be saved
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True, None
    except Exception as e:
        return False, f"Error saving HTML: {str(e)}"


def download_html_to_file(url: str, output_path: Path, timeout: int = 30) -> Tuple[bool, Optional[str]]:
    """
    Download HTML from a URL and save it to a file.
    
    Args:
        url: The URL to download HTML from
        output_path: Path where the file should be saved
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success, error_message)
    """
    html_content, error = download_html(url, timeout)
    
    if error:
        return False, error
    
    return save_html_to_file(html_content, output_path)
