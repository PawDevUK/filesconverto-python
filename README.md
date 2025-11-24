# PDF to DOC/DOCX Converter

Implementation of sections 1 through 10 from `convertion_process.md`

## Overview

This project implements the complete PDF to DOCX conversion logic described in the technical specification document. It covers all major aspects from file reading to DOCX generation.

### Implemented Features (Sections 1-10)

1. **File Upload and Reading Process (Section 1)**
   - Binary file reading
   - File validation
   - PDF header verification

2. **PDF File Format Structure (Section 2.1-2.4)**
   - PDF version extraction
   - Object extraction and parsing
   - Cross-reference table parsing
   - Dictionary parsing
   - Content stream identification

3. **PDF Compression (Section 2.5)**
   - FlateDecode (ZLIB/Deflate) decompression
   - Multiple compression method detection
   - Stream processing and decompression

4. **Text Extraction (Section 6)**
   - Text extraction from content streams
   - Text encoding handling (UTF-16, Latin-1, UTF-8)
   - Escape sequence processing
   - Stateful text extraction with formatting

5. **Font Detection and Extraction (Section 7)**
   - Font resource extraction
   - Font object parsing
   - PDF to Word font mapping
   - Font style detection (bold, italic)

6. **Color Extraction (Section 8)**
   - RGB, CMYK, and Grayscale color extraction
   - Color space conversion
   - Text color association
   - Hex color conversion for Word

7. **Background and Layout Processing (Section 9)**
   - Page dimension extraction
   - Background color extraction
   - Text positioning
   - Layout reconstruction
   - Paragraph detection

8. **DOCX Generation (Section 10)**
   - Complete DOCX XML structure generation
   - Document.xml with formatting
   - Content types and relationships
   - Styles and font tables
   - ZIP archive assembly

## Project Structure

```
filesconverto_python/
├── file_handler.py       # Section 1: File upload, reading, validation
├── pdf_parser.py         # Section 2.1-2.4: PDF structure parsing
├── pdf_compression.py    # Section 2.5: PDF compression handling
├── text_extractor.py     # Section 6: Text extraction with formatting
├── font_handler.py       # Section 7: Font detection and mapping
├── color_processor.py    # Section 8: Color extraction and conversion
├── layout_processor.py   # Section 9: Layout reconstruction
├── docx_generator.py     # Section 10: DOCX file generation
├── main.py              # Main orchestrator
├── create_test_pdf.py   # Test PDF generator
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Modules

### file_handler.py

Implements sections 1.1-1.3:

- `FileHandler.read_binary_file()` - Binary file reading
- `FileHandler.validate_pdf()` - PDF validation
- `FileHandler.get_file_info()` - File metadata extraction

### pdf_parser.py

Implements sections 2.1-2.4:

- `PDFParser.extract_pdf_version()` - PDF version detection
- `PDFParser.extract_objects()` - Object extraction
- `PDFParser.parse_xref()` - Cross-reference table parsing
- `PDFParser.parse_pdf_dictionary()` - Dictionary parsing
- `PDFParser.find_content_streams()` - Content stream identification

### pdf_compression.py

Implements section 2.5:

- `PDFCompression.decompress_flate()` - FlateDecode decompression
- `PDFCompression.decompress_stream()` - Generic stream decompression
- `PDFCompression.process_all_streams()` - Batch stream processing
- `PDFCompression.get_compression_info()` - Compression analysis

## Usage

### Basic Usage

```bash
python main.py <path_to_pdf_file> [output_file]
```

### Examples

```bash
# Convert PDF to DOCX (auto-generate output name)
python main.py sample.pdf

# Convert PDF to DOCX with custom output name
python main.py sample.pdf output.docx
```

### Complete Workflow

The program will:

1. Load and validate the PDF file (Section 1)
2. Extract PDF version and structure information (Section 2)
3. Parse all PDF objects and content streams
4. Decompress compressed streams (Section 2.5)
5. Extract text with formatting information (Section 6)
6. Process fonts and map to Word fonts (Section 7)
7. Extract and convert colors (Section 8)
8. Reconstruct layout and detect paragraphs (Section 9)
9. Generate complete DOCX file (Section 10)

### Sample Output

```
============================================================
PDF TO DOCX CONVERTER
Implementing sections 1 through 10
============================================================
Loading PDF file: sample.pdf
File size: 45632 bytes
Header: %PDF-1.7
Valid PDF: True

Parsing PDF structure...
PDF Version: 1.7
Total objects: 23
Content streams: 5

Decompressing PDF streams...
Total streams: 5
Compressed streams: 4
Uncompressed streams: 1
Compression methods: {'/FlateDecode': 4}
Successfully processed 5 streams

Extracting text content with formatting...
Extracted 42 text items

Generating DOCX file: sample.docx
✓ DOCX file created successfully: sample.docx

============================================================
SUCCESS: PDF to DOCX conversion complete!
Output file: sample.docx
============================================================
```

Total streams: 5
Compressed streams: 4
Uncompressed streams: 1
Compression methods: {'/FlateDecode': 4}
Successfully processed 5 streams

============================================================
DECOMPRESSED CONTENT ANALYSIS
============================================================

--- Object 4 ---
Content preview: BT\n/F1 12 Tf\n100 700 Td\n(Hello World) Tj\nET\n...

============================================================
SUCCESS: PDF processing complete through section 2.5
============================================================

```

## Implementation Details

### Section 1: File Upload and Reading
- Uses Python's built-in `open()` with binary mode (`'rb'`)
- Validates PDF signature (`%PDF-`)
- Checks for EOF marker (`%%EOF`)

### Section 2.1-2.4: PDF Structure
- Extracts PDF version from header
- Uses regex to parse PDF objects (`N M obj ... endobj`)
- Parses cross-reference table (`xref`) for object offsets
- Extracts dictionaries (`<< ... >>`)
- Identifies content streams containing page content

### Section 2.5: Compression
- Implements FlateDecode using Python's `zlib` module
- Handles both standard and raw deflate formats
- Identifies compression filters in stream dictionaries
- Supports multiple compression method detection
- Provides fallback for unsupported formats

### Section 6: Text Extraction
- Extracts text from decompressed content streams
- Handles multiple text encodings (UTF-16, Latin-1, UTF-8)
- Processes PDF escape sequences (\n, \r, \t, etc.)
- Tracks formatting state (font, size, color) while extracting
- Associates colors with text runs

### Section 7: Font Handling
- Parses font resources and font objects
- Maps PDF fonts to Word-compatible fonts
- Detects font styles (bold, italic) from font names
- Supports standard 14 PDF fonts
- Handles embedded and referenced fonts

### Section 8: Color Processing
- Extracts RGB, CMYK, and Grayscale colors
- Converts all color spaces to RGB hex format
- Tracks fill and stroke colors
- Associates colors with text for Word formatting

### Section 9: Layout Processing
- Extracts page dimensions (MediaBox)
- Identifies background rectangles and colors
- Tracks text positioning (Tm, Td operators)
- Reconstructs reading order from positioned text
- Detects paragraph boundaries based on spacing

### Section 10: DOCX Generation
- Creates complete DOCX XML structure
- Generates document.xml with formatted paragraphs
- Creates content types and relationships files
- Generates styles.xml and fontTable.xml
- Assembles ZIP archive (DOCX format)

## Technical Notes

### Dependencies
- **Python 3.7+** required
- **zlib** (built-in) for FlateDecode compression
- **zipfile** (built-in) for DOCX generation
- No external libraries needed for core functionality

### What's Implemented
✅ File reading and validation  
✅ PDF structure parsing  
✅ Object extraction  
✅ Stream identification and decompression  
✅ Text extraction with formatting  
✅ Font detection and mapping  
✅ Color extraction and conversion  
✅ Layout reconstruction  
✅ Paragraph detection  
✅ Complete DOCX generation  

### Known Limitations
❌ Complex multi-column layouts  
❌ Tables (extracted as text)  
❌ Embedded images  
❌ Vector graphics  
❌ Form fields  
❌ Hyperlinks  
❌ Annotations  
❌ LZW, ASCII85, CCITT compression  
❌ Encrypted/password-protected PDFs  
❌ Scanned PDFs (no OCR)  

## Testing

To test the implementation, you need a sample PDF file:

```bash
# Test with any PDF file
python main.py path/to/your/file.pdf
```

The program will process the PDF and display:

- File validation results
- PDF structure information
- Compression analysis
- Decompressed content preview

## Future Work (Beyond Section 2.5)

According to `convertion_process.md`, the following sections remain:

- Section 3: DOC File Format Structure
- Section 4: DOCX File Format Structure
- Section 5: PDF Parsing Process (continued)
- Section 6: Text Extraction from PDF
- Section 7: Font Detection and Extraction
- Section 8: Color Extraction
- Section 9: Background and Layout Processing
- Section 10: DOC/DOCX Generation

## License

This implementation is based on the technical specification in `convertion_process.md`.

## Notes

This is a vanilla Python implementation using only standard library modules:

- `zlib` - For FlateDecode compression
- `re` - For regex pattern matching
- `typing` - For type hints
- `sys`, `pathlib` - For file handling
