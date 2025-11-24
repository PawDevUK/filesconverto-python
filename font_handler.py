"""
Font Handling Module
Implements section 7 from convertion_process.md
"""

from typing import Dict, List, Any, Optional


class FontHandler:
    """Handles PDF font detection, extraction, and mapping"""

    # Standard PDF to Word font mapping
    FONT_MAPPING = {
        "Times-Roman": "Times New Roman",
        "Times-Bold": "Times New Roman",
        "Times-Italic": "Times New Roman",
        "Times-BoldItalic": "Times New Roman",
        "Helvetica": "Arial",
        "Helvetica-Bold": "Arial",
        "Helvetica-Oblique": "Arial",
        "Helvetica-BoldOblique": "Arial",
        "Courier": "Courier New",
        "Courier-Bold": "Courier New",
        "Courier-Oblique": "Courier New",
        "Courier-BoldOblique": "Courier New",
        "Symbol": "Symbol",
        "ZapfDingbats": "Wingdings",
    }

    @staticmethod
    def parse_font_object(font_obj: bytes) -> Dict[str, Any]:
        """
        Parse font object to extract font information
        Section 7.2: Font Object Structure

        Args:
            font_obj: Font object content from PDF

        Returns:
            Dict: Font information
        """
        from pdf_parser import PDFParser

        font_dict = PDFParser.parse_pdf_dictionary(font_obj)

        font_info = {
            "Type": font_dict.get("Type", b""),  # Should be '/Font'
            "Subtype": font_dict.get("Subtype", b""),  # Type1, TrueType, etc.
            "BaseFont": font_dict.get("BaseFont", b""),  # Font name
            "Encoding": font_dict.get("Encoding", b""),  # Character encoding
        }

        # Extract base font name (e.g., '/Arial-Bold')
        base_font = font_info["BaseFont"]
        if isinstance(base_font, bytes) and base_font.startswith(b"/"):
            font_name = base_font[1:].decode("latin-1", errors="ignore")
            font_info["FontName"] = font_name
        elif isinstance(base_font, str) and base_font.startswith("/"):
            font_info["FontName"] = base_font[1:]
        else:
            font_info["FontName"] = "Unknown"

        return font_info

    @staticmethod
    def extract_font_info_from_stream(stream_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract font and size information from content stream
        Section 7.4: Font Size Extraction

        Args:
            stream_data: Decompressed content stream

        Returns:
            List[Dict]: Font specifications found in stream
        """
        font_specifications = []

        # Pattern: /FontName FontSize Tf
        # Example: /F1 12 Tf

        lines = stream_data.split(b"\n")
        for line in lines:
            tokens = line.split()
            for i in range(len(tokens) - 2):
                if tokens[i + 2] == b"Tf":
                    try:
                        font_name = tokens[i].decode("latin-1")  # e.g., '/F1'
                        font_size = float(tokens[i + 1])  # e.g., 12

                        font_specifications.append(
                            {"font": font_name, "size": font_size}
                        )
                    except (ValueError, UnicodeDecodeError):
                        pass

        return font_specifications

    @staticmethod
    def map_pdf_font_to_word(pdf_font_name: str) -> str:
        """
        Map PDF font names to Word-compatible font names
        Section 7.5: Font Mapping

        Args:
            pdf_font_name: PDF font name (e.g., 'Helvetica-Bold')

        Returns:
            str: Word-compatible font name
        """
        # Remove leading slash if present
        clean_name = pdf_font_name.lstrip("/")

        # Check if it's in our mapping
        if clean_name in FontHandler.FONT_MAPPING:
            return FontHandler.FONT_MAPPING[clean_name]

        # Check for font family extraction
        # Many fonts are named like 'Arial-Bold' or 'TimesNewRomanPS-BoldMT'
        for pdf_name, word_name in FontHandler.FONT_MAPPING.items():
            base_name = pdf_name.split("-")[0]
            if clean_name.startswith(base_name):
                return word_name

        # Try to extract base font family
        # Remove common suffixes
        base_font = clean_name.split("-")[0].split(",")[0]

        # Check if base matches known fonts
        if "Times" in base_font:
            return "Times New Roman"
        elif "Helvetica" in base_font or "Arial" in base_font:
            return "Arial"
        elif "Courier" in base_font:
            return "Courier New"

        # Default fallback
        return "Calibri"

    @staticmethod
    def detect_font_style(font_name: str) -> Dict[str, bool]:
        """
        Detect bold/italic from font name
        Section 7.6: Font Style Detection

        Args:
            font_name: Font name to analyze

        Returns:
            Dict: Style flags (bold, italic)
        """
        font_name_upper = font_name.upper()

        # Detect bold
        is_bold = any(
            keyword in font_name_upper
            for keyword in ["BOLD", "-B", ",B", "-BD", "HEAVY", "BLACK"]
        )

        # Detect italic
        is_italic = any(
            keyword in font_name_upper
            for keyword in ["ITALIC", "OBLIQUE", "-I", ",I", "-IT", "SLANT"]
        )

        return {"bold": is_bold, "italic": is_italic}

    @staticmethod
    def extract_all_fonts(content_streams: List[Dict[str, Any]]) -> List[str]:
        """
        Extract all unique fonts from content streams

        Args:
            content_streams: List of content stream dictionaries

        Returns:
            List[str]: Unique font names
        """
        fonts = set()

        for stream_info in content_streams:
            stream_data = stream_info.get("stream", b"")
            if isinstance(stream_data, bytes):
                font_specs = FontHandler.extract_font_info_from_stream(stream_data)
                for spec in font_specs:
                    font = spec.get("font", "")
                    if font:
                        # Map to Word font
                        word_font = FontHandler.map_pdf_font_to_word(font)
                        fonts.add(word_font)

        return sorted(list(fonts)) if fonts else ["Calibri"]
