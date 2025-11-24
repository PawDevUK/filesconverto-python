"""
Text Extraction Module
Implements section 6 from convertion_process.md
"""

from typing import List, Dict, Any, Tuple
import re


class PDFTextExtractor:
    """Stateful PDF text extractor that tracks formatting"""

    def __init__(self):
        """Initialize text extractor with default state"""
        self.current_font = None
        self.current_font_size = 12
        self.current_fill_color = (0, 0, 0)  # Black
        self.current_stroke_color = (0, 0, 0)
        self.text_items: List[Dict[str, Any]] = []

    @staticmethod
    def extract_text_from_stream(stream_data: bytes) -> List[str]:
        """
        Extract text from PDF content stream
        Section 6.3: Text Extraction from Content Stream

        Args:
            stream_data: Decompressed PDF stream data

        Returns:
            List[str]: Extracted text strings
        """
        text_content = []

        # Look for text operations
        # Text is enclosed in parentheses: (Text)
        in_text_block = False

        i = 0
        while i < len(stream_data):
            # Check for BT (Begin Text)
            if stream_data[i : i + 2] == b"BT":
                in_text_block = True
                i += 2
                continue

            # Check for ET (End Text)
            if stream_data[i : i + 2] == b"ET":
                in_text_block = False
                i += 2
                continue

            # Extract text in parentheses
            if stream_data[i : i + 1] == b"(":
                # Find matching closing parenthesis
                j = i + 1
                escape = False
                while j < len(stream_data):
                    if stream_data[j : j + 1] == b"\\" and not escape:
                        escape = True
                        j += 1
                        continue
                    if stream_data[j : j + 1] == b")" and not escape:
                        break
                    escape = False
                    j += 1

                text_bytes = stream_data[i + 1 : j]
                # Decode text (might be ASCII, UTF-16, or other encoding)
                text = PDFTextExtractor.decode_pdf_text(text_bytes)
                if text:
                    text_content.append(text)

                i = j + 1
            else:
                i += 1

        return text_content

    @staticmethod
    def decode_pdf_text(text_bytes: bytes, encoding: str = "latin-1") -> str:
        """
        Decode PDF text with proper encoding
        Section 6.4: Text Encoding Handling

        Args:
            text_bytes: Raw bytes from PDF
            encoding: Default encoding to try

        Returns:
            str: Decoded text
        """
        # Check for BOM (Byte Order Mark) for UTF-16
        if text_bytes.startswith(b"\xfe\xff"):
            # UTF-16 Big Endian
            return text_bytes[2:].decode("utf-16-be", errors="ignore")
        elif text_bytes.startswith(b"\xff\xfe"):
            # UTF-16 Little Endian
            return text_bytes[2:].decode("utf-16-le", errors="ignore")

        # Try standard encodings
        encodings = ["latin-1", "utf-8", "cp1252"]
        for enc in encodings:
            try:
                return text_bytes.decode(enc)
            except UnicodeDecodeError:
                continue

        # Fallback: decode with errors ignored
        return text_bytes.decode("latin-1", errors="ignore")

    @staticmethod
    def unescape_pdf_string(text: str) -> str:
        """
        Handle PDF string escape sequences
        Section 6.5: Escape Sequence Handling

        Args:
            text: Text with escape sequences

        Returns:
            str: Unescaped text
        """
        result = []
        i = 0
        while i < len(text):
            if text[i] == "\\" and i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == "n":
                    result.append("\n")
                    i += 2
                elif next_char == "r":
                    result.append("\r")
                    i += 2
                elif next_char == "t":
                    result.append("\t")
                    i += 2
                elif next_char == "b":
                    result.append("\b")
                    i += 2
                elif next_char == "f":
                    result.append("\f")
                    i += 2
                elif next_char == "(":
                    result.append("(")
                    i += 2
                elif next_char == ")":
                    result.append(")")
                    i += 2
                elif next_char == "\\":
                    result.append("\\")
                    i += 2
                elif next_char.isdigit():
                    # Octal code (up to 3 digits)
                    octal = text[i + 1 : i + 4]
                    octal_digits = ""
                    for c in octal:
                        if c.isdigit():
                            octal_digits += c
                        else:
                            break
                    if octal_digits:
                        try:
                            char_code = int(octal_digits, 8)
                            result.append(chr(char_code))
                            i += 1 + len(octal_digits)
                        except ValueError:
                            result.append(text[i])
                            i += 1
                    else:
                        result.append(text[i])
                        i += 1
                else:
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1

        return "".join(result)

    def process_stream(self, stream_data: bytes) -> List[Dict[str, Any]]:
        """
        Process content stream and track text with formatting
        Section 8.4: Text Color Association (combined with text extraction)

        Args:
            stream_data: Decompressed PDF stream data

        Returns:
            List[Dict]: Text items with formatting information
        """
        self.text_items = []
        lines = stream_data.split(b"\n")

        for line in lines:
            tokens = line.split()

            # Font setting: /F1 12 Tf
            if len(tokens) >= 3 and tokens[-1] == b"Tf":
                try:
                    self.current_font = tokens[-3].decode("latin-1")
                    self.current_font_size = float(tokens[-2])
                except (ValueError, UnicodeDecodeError):
                    pass

            # Fill color: r g b rg
            elif len(tokens) >= 4 and tokens[-1] == b"rg":
                try:
                    r = float(tokens[-4])
                    g = float(tokens[-3])
                    b = float(tokens[-2])
                    self.current_fill_color = (r, g, b)
                except (ValueError, IndexError):
                    pass

            # Text showing: (Text) Tj
            elif b"(" in line and b")" in line and b"Tj" in line:
                # Extract text
                start = line.find(b"(")
                end = line.rfind(b")")
                if start != -1 and end != -1 and start < end:
                    text_bytes = line[start + 1 : end]
                    text = self.decode_pdf_text(text_bytes)
                    text = self.unescape_pdf_string(text)

                    # Store text with formatting
                    self.text_items.append(
                        {
                            "text": text,
                            "font": self.current_font,
                            "size": self.current_font_size,
                            "color": self.current_fill_color,
                        }
                    )

        return self.text_items

    @staticmethod
    def extract_all_text_simple(stream_data: bytes) -> str:
        """
        Simple text extraction without formatting

        Args:
            stream_data: Decompressed PDF stream data

        Returns:
            str: All extracted text joined with spaces
        """
        text_parts = PDFTextExtractor.extract_text_from_stream(stream_data)
        return " ".join(text_parts)

    @staticmethod
    def extract_text_with_positions(stream_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract text with position information
        Section 9.3: Text Positioning

        Args:
            stream_data: Decompressed PDF stream data

        Returns:
            List[Dict]: Text with position information
        """
        text_positions = []

        current_x = 0.0
        current_y = 0.0

        lines = stream_data.split(b"\n")
        for line in lines:
            tokens = line.split()

            # Text matrix: a b c d e f Tm
            # Simplified: e and f are x,y position
            if len(tokens) >= 7 and tokens[-1] == b"Tm":
                try:
                    current_x = float(tokens[-3])
                    current_y = float(tokens[-2])
                except (ValueError, IndexError):
                    pass

            # Text positioning: tx ty Td
            elif len(tokens) >= 3 and tokens[-1] == b"Td":
                try:
                    tx = float(tokens[-3])
                    ty = float(tokens[-2])
                    current_x += tx
                    current_y += ty
                except (ValueError, IndexError):
                    pass

            # Text showing with position
            elif b"(" in line and b")" in line:
                start = line.find(b"(")
                end = line.rfind(b")")
                if start != -1 and end != -1 and start < end:
                    text_bytes = line[start + 1 : end]
                    text = PDFTextExtractor.decode_pdf_text(text_bytes)
                    text = PDFTextExtractor.unescape_pdf_string(text)

                    text_positions.append(
                        {"text": text, "x": current_x, "y": current_y}
                    )

        return text_positions
