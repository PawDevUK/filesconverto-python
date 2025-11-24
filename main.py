"""
PDF to DOC/DOCX Converter - Main Application
Orchestrates the conversion process using modules from sections 1-10
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from file_handler import FileHandler
from pdf_parser import PDFParser
from pdf_compression import PDFCompression
from text_extractor import PDFTextExtractor
from font_handler import FontHandler
from color_processor import ColorProcessor
from layout_processor import LayoutProcessor
from docx_generator import DOCXGenerator


class PDFConverter:
    """Main PDF conversion orchestrator"""

    def __init__(self, input_file: str, output_file: str = None):
        """
        Initialize converter with input file

        Args:
            input_file: Path to input PDF file
            output_file: Path to output DOCX file (optional)
        """
        self.input_file = input_file
        self.output_file = output_file or input_file.replace(".pdf", ".docx")
        self.pdf_data: Optional[bytes] = None
        self.pdf_structure: Optional[dict] = None
        self.processed_streams: Optional[dict] = None
        self.extracted_content: List[Dict[str, Any]] = []

    def load_and_validate(self) -> bool:
        """
        Load and validate PDF file (Section 1.1-1.3)

        Returns:
            bool: True if file is valid, False otherwise
        """
        print(f"Loading PDF file: {self.input_file}")

        try:
            # Use FileHandler to upload and validate
            self.pdf_data, is_valid, info = FileHandler.upload_and_validate(
                self.input_file
            )

            print(f"File size: {info['file_size']} bytes")
            print(f"Header: {info['header']}")
            print(f"Valid PDF: {is_valid}")

            return is_valid

        except FileNotFoundError:
            print(f"Error: File not found: {self.input_file}")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def parse_structure(self) -> bool:
        """
        Parse PDF structure (Section 2.1-2.4)

        Returns:
            bool: True if parsing successful
        """
        if not self.pdf_data:
            print("Error: No PDF data loaded")
            return False

        print("\nParsing PDF structure...")

        try:
            # Use PDFParser to parse structure
            self.pdf_structure = PDFParser.parse_pdf_structure(self.pdf_data)

            print(f"PDF Version: {self.pdf_structure['version']}")
            print(f"Total objects: {self.pdf_structure['total_objects']}")
            print(f"Content streams: {self.pdf_structure['total_streams']}")

            return True

        except Exception as e:
            print(f"Error parsing PDF structure: {e}")
            return False

    def decompress_streams(self) -> bool:
        """
        Decompress PDF streams (Section 2.5)

        Returns:
            bool: True if decompression successful
        """
        if not self.pdf_structure:
            print("Error: PDF structure not parsed")
            return False

        print("\nDecompressing PDF streams...")

        try:
            content_streams = self.pdf_structure["content_streams"]

            # Get compression info
            compression_info = PDFCompression.get_compression_info(content_streams)
            print(f"Total streams: {compression_info['total_streams']}")
            print(f"Compressed streams: {compression_info['compressed_streams']}")
            print(f"Uncompressed streams: {compression_info['uncompressed_streams']}")
            print(f"Compression methods: {compression_info['compression_methods']}")

            # Process all streams
            self.processed_streams = PDFCompression.process_all_streams(content_streams)
            print(f"Successfully processed {len(self.processed_streams)} streams")

            return True

        except Exception as e:
            print(f"Error decompressing streams: {e}")
            return False

    def extract_text_content(self) -> bool:
        """
        Extract text with formatting from streams (Section 6)

        Returns:
            bool: True if successful
        """
        if not self.processed_streams:
            print("Error: No processed streams available")
            return False

        print("\nExtracting text content with formatting...")

        try:
            all_text_items = []

            for obj_num, stream_data in self.processed_streams.items():
                # Extract text with formatting
                extractor = PDFTextExtractor()
                text_items = extractor.process_stream(stream_data)

                # Extract font information
                font_specs = FontHandler.extract_font_info_from_stream(stream_data)

                # Process each text item
                for item in text_items:
                    # Map font to Word font
                    if item.get("font"):
                        word_font = FontHandler.map_pdf_font_to_word(item["font"])
                        item["font"] = word_font

                        # Detect font style
                        style = FontHandler.detect_font_style(item["font"])
                        item["bold"] = style["bold"]
                        item["italic"] = style["italic"]

                    # Convert color to hex
                    if item.get("color"):
                        color_info = {"space": "RGB", "values": item["color"]}
                        item["color"] = ColorProcessor.convert_color_to_hex(color_info)

                    all_text_items.append(item)

            self.extracted_content = all_text_items
            print(f"Extracted {len(all_text_items)} text items")

            return True

        except Exception as e:
            print(f"Error extracting text: {e}")
            import traceback

            traceback.print_exc()
            return False

    def generate_docx(self) -> bool:
        """
        Generate DOCX file from extracted content (Section 10)

        Returns:
            bool: True if successful
        """
        print(f"\nGenerating DOCX file: {self.output_file}")

        try:
            # Extract unique fonts
            fonts = (
                FontHandler.extract_all_fonts(
                    self.pdf_structure.get("content_streams", [])
                )
                if self.pdf_structure
                else ["Calibri"]
            )

            # If no content extracted, create simple document with extracted text
            if not self.extracted_content:
                print(
                    "Warning: No formatted content extracted, creating simple document"
                )

                # Try simple text extraction
                simple_text = []
                for obj_num, stream_data in self.processed_streams.items():
                    text_parts = PDFTextExtractor.extract_text_from_stream(stream_data)
                    simple_text.extend(text_parts)

                combined_text = (
                    " ".join(simple_text)
                    if simple_text
                    else "No text could be extracted from PDF"
                )
                DOCXGenerator.create_docx_from_text(combined_text, self.output_file)
            else:
                # Create DOCX with formatting
                DOCXGenerator.create_docx_file(
                    self.extracted_content, self.output_file, fonts
                )

            print(f"✓ DOCX file created successfully: {self.output_file}")
            return True

        except Exception as e:
            print(f"Error generating DOCX: {e}")
            import traceback

            traceback.print_exc()
            return False

    def analyze_content(self) -> None:
        """
        Analyze decompressed content (for debugging)
        """
        if not self.processed_streams:
            print("No processed streams available")
            return

        print("\n" + "=" * 60)
        print("DECOMPRESSED CONTENT ANALYSIS")
        print("=" * 60)

        for obj_num, stream_data in self.processed_streams.items():
            print(f"\n--- Object {obj_num} ---")
            # Try to decode as text
            try:
                text = stream_data.decode("latin-1")
                # Show first 200 characters
                preview = text[:200].replace("\n", "\\n")
                print(f"Content preview: {preview}")
                if len(text) > 200:
                    print(f"... ({len(text)} total characters)")
            except UnicodeDecodeError:
                print(f"Binary data: {len(stream_data)} bytes")

    def run(self) -> bool:
        """
        Run complete conversion process (sections 1-10)

        Returns:
            bool: True if successful
        """
        print("=" * 60)
        print("PDF TO DOCX CONVERTER")
        print("Implementing sections 1 through 10")
        print("=" * 60)

        # Step 1: Load and validate (Section 1)
        if not self.load_and_validate():
            print("\nFailed: File validation")
            return False

        # Step 2: Parse structure (Section 2.1-2.4)
        if not self.parse_structure():
            print("\nFailed: PDF structure parsing")
            return False

        # Step 3: Decompress streams (Section 2.5)
        if not self.decompress_streams():
            print("\nFailed: Stream decompression")
            return False

        # Step 4: Extract text with formatting (Section 6-9)
        if not self.extract_text_content():
            print(
                "\nWarning: Text extraction had issues, will attempt simple conversion"
            )

        # Step 5: Generate DOCX (Section 10)
        if not self.generate_docx():
            print("\nFailed: DOCX generation")
            return False

        # Optional: Analyze content for debugging
        # self.analyze_content()

        print("\n" + "=" * 60)
        print("SUCCESS: PDF to DOCX conversion complete!")
        print(f"Output file: {self.output_file}")
        print("=" * 60)

        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_file> [output_file]")
        print("Example: python main.py sample.pdf")
        print("Example: python main.py sample.pdf output.docx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if file exists
    if not Path(input_file).exists():
        print(f"Error: File does not exist: {input_file}")
        sys.exit(1)

    # Create converter and run
    converter = PDFConverter(input_file, output_file)
    success = converter.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
