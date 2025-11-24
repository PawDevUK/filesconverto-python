"""
PDF Downloader for Project Gutenberg

This script downloads PDFs from Project Gutenberg for testing the PDF to DOCX conversion
application. The PDFs are saved to the 'samples' directory.

Test Coverage (from pdf_test_sources_report.md - Section 1.1 Project Gutenberg):
- Simple text extraction and conversion
- Plain text with minimal formatting
- Various document lengths
- Basic text features (paragraphs, chapters, etc.)

What to Test:
- Plain text extraction
- Different font families
- Different font sizes
- Headers and footers
- Page numbers
- Text alignment
"""

import requests
from pathlib import Path
from typing import Optional


# Book IDs from Project Gutenberg with their titles
# These cover various lengths and text styles for testing simple text extraction
GUTENBERG_BOOKS = {
    1342: "Pride and Prejudice",
    11: "Alice's Adventures in Wonderland",
    84: "Frankenstein",
    1661: "The Adventures of Sherlock Holmes",
    98: "A Tale of Two Cities",
    1260: "Jane Eyre",
    345: "Dracula",
    46: "A Christmas Carol",
    74: "The Adventures of Tom Sawyer",
    76: "Adventures of Huckleberry Finn",
    1080: "A Modest Proposal",
    244: "A Study in Scarlet",
    2814: "Dubliners",
    43: "The Strange Case of Dr Jekyll and Mr Hyde",
    1232: "The Prince",
    158: "Emma",
    161: "Sense and Sensibility",
    768: "Wuthering Heights",
    5200: "Metamorphosis",
    215: "The Call of the Wild",
    219: "Heart of Darkness",
    1400: "Great Expectations",
    16: "Peter Pan",
    1184: "The Count of Monte Cristo",
    120: "Treasure Island",
    55: "The Wonderful Wizard of Oz",
    174: "The Picture of Dorian Gray",
    844: "The Importance of Being Earnest",
    1497: "The Republic",
    514: "Little Women",
    145: "Middlemarch",
    160: "The Awakening",
    205: "Walden",
    829: "Gulliver's Travels",
    1727: "The Odyssey",
    2600: "War and Peace",
    2554: "Crime and Punishment",
    1399: "Anna Karenina",
    2591: "Grimms' Fairy Tales",
    41: "The Legend of Sleepy Hollow",
    236: "The Jungle Book",
    19337: "The Brothers Karamazov",
    408: "The Soul of Man under Socialism",
    135: "Les Miserables",
    996: "Don Quixote",
    4300: "Ulysses",
    1952: "The Yellow Wallpaper",
    2701: "Moby Dick",
    64317: "The Great Gatsby",
    100: "The Complete Works of William Shakespeare",
}


def get_samples_directory() -> Path:
    """Get the path to the samples directory."""
    script_dir = Path(__file__).parent
    samples_dir = script_dir / "samples"
    samples_dir.mkdir(exist_ok=True)
    return samples_dir


def get_gutenberg_pdf_url(book_id: int) -> str:
    """
    Construct the URL for downloading a PDF from Project Gutenberg.
    
    Project Gutenberg provides PDFs at predictable URLs based on book ID.
    The URL pattern is: https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf
    
    Some books may have alternative URL patterns:
    - https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.pdf
    """
    return f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.pdf"


def download_pdf(book_id: int, output_dir: Path, timeout: int = 30) -> Optional[Path]:
    """
    Download a PDF from Project Gutenberg.
    
    Args:
        book_id: The Project Gutenberg book ID
        output_dir: Directory to save the PDF
        timeout: Request timeout in seconds
        
    Returns:
        Path to the downloaded file, or None if download failed
    """
    title = GUTENBERG_BOOKS.get(book_id, f"Unknown Book {book_id}")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"gutenberg_{book_id}_{safe_title[:50]}.pdf"
    output_path = output_dir / filename
    
    # Skip if already downloaded
    if output_path.exists():
        print(f"  [SKIP] Already downloaded: {filename}")
        return output_path
    
    url = get_gutenberg_pdf_url(book_id)
    
    try:
        print(f"  [DOWNLOAD] {title} (ID: {book_id})...")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Check if it's actually a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not response.content[:4] == b'%PDF':
            print(f"  [ERROR] Not a PDF: {title}")
            return None
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = output_path.stat().st_size / 1024  # Size in KB
        print(f"  [SUCCESS] Downloaded: {filename} ({file_size:.1f} KB)")
        return output_path
        
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Timeout downloading: {title}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  [ERROR] HTTP error for {title}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Failed to download {title}: {e}")
        return None


def download_all_books(max_count: Optional[int] = None) -> dict:
    """
    Download all configured books from Project Gutenberg.
    
    Args:
        max_count: Maximum number of books to download (None for all)
        
    Returns:
        Dictionary with 'success' and 'failed' lists
    """
    samples_dir = get_samples_directory()
    
    print(f"\n{'='*60}")
    print("Project Gutenberg PDF Downloader")
    print(f"{'='*60}")
    print(f"Output directory: {samples_dir}")
    print(f"Total books configured: {len(GUTENBERG_BOOKS)}")
    
    if max_count:
        print(f"Limiting download to: {max_count} books")
    
    print(f"{'='*60}\n")
    
    results = {'success': [], 'failed': []}
    book_ids = list(GUTENBERG_BOOKS.keys())
    
    if max_count:
        book_ids = book_ids[:max_count]
    
    for i, book_id in enumerate(book_ids, 1):
        print(f"[{i}/{len(book_ids)}]", end="")
        result = download_pdf(book_id, samples_dir)
        
        if result:
            results['success'].append((book_id, GUTENBERG_BOOKS[book_id], result))
        else:
            results['failed'].append((book_id, GUTENBERG_BOOKS[book_id]))
    
    # Print summary
    print(f"\n{'='*60}")
    print("Download Summary")
    print(f"{'='*60}")
    print(f"Successfully downloaded: {len(results['success'])} files")
    print(f"Failed downloads: {len(results['failed'])} files")
    
    if results['failed']:
        print("\nFailed downloads:")
        for book_id, title in results['failed']:
            print(f"  - {title} (ID: {book_id})")
    
    print(f"{'='*60}\n")
    
    return results


def list_downloaded_pdfs() -> list:
    """List all downloaded PDFs in the samples directory."""
    samples_dir = get_samples_directory()
    pdf_files = list(samples_dir.glob("*.pdf"))
    
    print(f"\nDownloaded PDFs in {samples_dir}:")
    print("-" * 40)
    
    for pdf in sorted(pdf_files):
        size = pdf.stat().st_size / 1024  # KB
        print(f"  {pdf.name} ({size:.1f} KB)")
    
    print(f"\nTotal: {len(pdf_files)} PDF files")
    return pdf_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download PDFs from Project Gutenberg for testing"
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=None,
        help="Maximum number of books to download (default: all)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List already downloaded PDFs"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_downloaded_pdfs()
    else:
        download_all_books(max_count=args.max_count)
