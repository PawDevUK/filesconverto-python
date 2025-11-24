"""
Color Processing Module
Implements section 8 from convertion_process.md
"""

from typing import Dict, List, Any, Tuple


class ColorProcessor:
    """Handles PDF color extraction and conversion"""

    @staticmethod
    def extract_colors_from_stream(stream_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract color information from content stream
        Section 8.2: Color Operators

        Args:
            stream_data: Decompressed content stream

        Returns:
            List[Dict]: Color specifications
        """
        colors = []

        lines = stream_data.split(b"\n")
        for line in lines:
            tokens = line.split()

            # RGB fill color: r g b rg
            if len(tokens) >= 4 and tokens[-1] == b"rg":
                try:
                    r = float(tokens[-4])
                    g = float(tokens[-3])
                    b = float(tokens[-2])
                    colors.append({"type": "fill", "space": "RGB", "values": (r, g, b)})
                except (ValueError, IndexError):
                    pass

            # RGB stroke color: r g b RG
            elif len(tokens) >= 4 and tokens[-1] == b"RG":
                try:
                    r = float(tokens[-4])
                    g = float(tokens[-3])
                    b = float(tokens[-2])
                    colors.append(
                        {"type": "stroke", "space": "RGB", "values": (r, g, b)}
                    )
                except (ValueError, IndexError):
                    pass

            # CMYK fill color: c m y k k
            elif len(tokens) >= 5 and tokens[-1] == b"k":
                try:
                    c = float(tokens[-5])
                    m = float(tokens[-4])
                    y = float(tokens[-3])
                    k_val = float(tokens[-2])
                    colors.append(
                        {"type": "fill", "space": "CMYK", "values": (c, m, y, k_val)}
                    )
                except (ValueError, IndexError):
                    pass

            # CMYK stroke color: c m y k K
            elif len(tokens) >= 5 and tokens[-1] == b"K":
                try:
                    c = float(tokens[-5])
                    m = float(tokens[-4])
                    y = float(tokens[-3])
                    k_val = float(tokens[-2])
                    colors.append(
                        {"type": "stroke", "space": "CMYK", "values": (c, m, y, k_val)}
                    )
                except (ValueError, IndexError):
                    pass

            # Gray fill: g g
            elif len(tokens) >= 2 and tokens[-1] == b"g":
                try:
                    gray = float(tokens[-2])
                    colors.append({"type": "fill", "space": "Gray", "values": (gray,)})
                except (ValueError, IndexError):
                    pass

            # Gray stroke: G G
            elif len(tokens) >= 2 and tokens[-1] == b"G":
                try:
                    gray = float(tokens[-2])
                    colors.append(
                        {"type": "stroke", "space": "Gray", "values": (gray,)}
                    )
                except (ValueError, IndexError):
                    pass

        return colors

    @staticmethod
    def convert_color_to_hex(color_info: Dict[str, Any]) -> str:
        """
        Convert PDF color to hex string for Word
        Section 8.3: Color Conversion

        Args:
            color_info: Color information dictionary

        Returns:
            str: Hex color string (e.g., 'FF0000')
        """
        color_space = color_info.get("space", "RGB")
        values = color_info.get("values", (0, 0, 0))

        if color_space == "RGB":
            r, g, b = values[0], values[1], values[2]
            # PDF uses 0-1 range, convert to 0-255
            r_int = int(r * 255)
            g_int = int(g * 255)
            b_int = int(b * 255)
            return f"{r_int:02X}{g_int:02X}{b_int:02X}"

        elif color_space == "CMYK":
            c, m, y, k = values[0], values[1], values[2], values[3]
            # Convert CMYK to RGB
            r = 255 * (1 - c) * (1 - k)
            g = 255 * (1 - m) * (1 - k)
            b = 255 * (1 - y) * (1 - k)
            return f"{int(r):02X}{int(g):02X}{int(b):02X}"

        elif color_space == "Gray":
            gray = values[0]
            gray_int = int(gray * 255)
            return f"{gray_int:02X}{gray_int:02X}{gray_int:02X}"

        return "000000"  # Default black

    @staticmethod
    def rgb_to_hex(r: float, g: float, b: float) -> str:
        """
        Convert RGB (0-1 range) to hex

        Args:
            r, g, b: RGB values in 0-1 range

        Returns:
            str: Hex color string
        """
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        return f"{r_int:02X}{g_int:02X}{b_int:02X}"

    @staticmethod
    def extract_background_from_stream(stream_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract background/fill operations
        Section 9.2: Background Color Extraction

        Args:
            stream_data: Decompressed content stream

        Returns:
            List[Dict]: Background rectangles with colors
        """
        backgrounds = []

        lines = stream_data.split(b"\n")
        i = 0

        current_fill_color = None

        while i < len(lines):
            line = lines[i]
            tokens = line.split()

            # Fill color setting
            if len(tokens) >= 4 and tokens[-1] == b"rg":
                try:
                    r = float(tokens[-4])
                    g = float(tokens[-3])
                    b = float(tokens[-2])
                    current_fill_color = (r, g, b)
                except (ValueError, IndexError):
                    pass

            # Rectangle: x y width height re
            elif len(tokens) >= 5 and tokens[-1] == b"re":
                try:
                    x = float(tokens[-5])
                    y = float(tokens[-4])
                    width = float(tokens[-3])
                    height = float(tokens[-2])

                    # Check next line for fill operator
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if b"f" in next_line or b"F" in next_line or b"B" in next_line:
                            # This rectangle is filled
                            backgrounds.append(
                                {
                                    "x": x,
                                    "y": y,
                                    "width": width,
                                    "height": height,
                                    "color": current_fill_color,
                                }
                            )
                except (ValueError, IndexError):
                    pass

            i += 1

        return backgrounds
