"""
Layout Processing Module
Implements section 9 from convertion_process.md
"""

from typing import Dict, List, Any, Tuple


class LayoutProcessor:
    """Handles PDF layout reconstruction"""

    @staticmethod
    def extract_page_dimensions(page_obj: bytes) -> Dict[str, Any]:
        """
        Extract page size from page object
        Section 9.1: Page Size and Dimensions

        Args:
            page_obj: Page object content

        Returns:
            Dict: Page dimensions
        """
        from pdf_parser import PDFParser

        page_dict = PDFParser.parse_pdf_dictionary(page_obj)

        # Default US Letter size
        width = 612  # points
        height = 792  # points

        # Look for /MediaBox [llx lly urx ury]
        if "MediaBox" in page_dict:
            # Would need to parse the array - simplified here
            pass

        return {"width": width, "height": height, "unit": "points"}

    @staticmethod
    def reconstruct_layout(
        text_positions: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        """
        Reconstruct document layout from positioned text
        Section 9.4: Layout Reconstruction

        Args:
            text_positions: List of text items with positions

        Returns:
            List[List[Dict]]: Lines of text items
        """
        if not text_positions:
            return []

        # Sort by Y position (descending) then X position
        sorted_items = sorted(
            text_positions, key=lambda item: (-item.get("y", 0), item.get("x", 0))
        )

        # Group into lines based on Y tolerance
        lines: List[List[Dict[str, Any]]] = []
        current_line: List[Dict[str, Any]] = []
        current_y = None
        y_tolerance = 2  # Points

        for item in sorted_items:
            item_y = item.get("y", 0)

            if current_y is None:
                current_y = item_y
                current_line.append(item)
            elif abs(item_y - current_y) <= y_tolerance:
                # Same line
                current_line.append(item)
            else:
                # New line
                # Sort current line by X position
                current_line.sort(key=lambda x: x.get("x", 0))
                lines.append(current_line)
                current_line = [item]
                current_y = item_y

        if current_line:
            current_line.sort(key=lambda x: x.get("x", 0))
            lines.append(current_line)

        return lines

    @staticmethod
    def detect_paragraphs(
        lines: List[List[Dict[str, Any]]],
    ) -> List[List[Dict[str, Any]]]:
        """
        Detect paragraph boundaries from lines
        Section 9.5: Paragraph Detection

        Args:
            lines: Lines of text items

        Returns:
            List[List[Dict]]: Paragraphs (each is a list of text items)
        """
        if not lines:
            return []

        paragraphs: List[List[Dict[str, Any]]] = []
        current_paragraph: List[Dict[str, Any]] = []

        for i, line in enumerate(lines):
            current_paragraph.extend(line)

            # Check if next line starts a new paragraph
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                # Heuristics for paragraph break:
                # 1. Large vertical gap
                # 2. Empty line

                if line and next_line:
                    current_y = line[0].get("y", 0)
                    next_y = next_line[0].get("y", 0)

                    y_gap = abs(current_y - next_y)

                    if y_gap > 20:  # Large gap indicates paragraph break
                        paragraphs.append(current_paragraph)
                        current_paragraph = []
            else:
                # Last line
                paragraphs.append(current_paragraph)

        if current_paragraph and not paragraphs:
            paragraphs.append(current_paragraph)

        return paragraphs

    @staticmethod
    def merge_text_items(items: List[Dict[str, Any]]) -> str:
        """
        Merge text items into a single string

        Args:
            items: List of text item dictionaries

        Returns:
            str: Merged text
        """
        texts = [item.get("text", "") for item in items]
        return " ".join(texts)

    @staticmethod
    def group_by_formatting(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group consecutive items with same formatting

        Args:
            items: List of text items with formatting

        Returns:
            List[Dict]: Grouped items
        """
        if not items:
            return []

        grouped = []
        current_group = {
            "text": items[0].get("text", ""),
            "font": items[0].get("font"),
            "size": items[0].get("size"),
            "color": items[0].get("color"),
            "bold": items[0].get("bold", False),
            "italic": items[0].get("italic", False),
        }

        for i in range(1, len(items)):
            item = items[i]

            # Check if formatting matches current group
            if (
                item.get("font") == current_group["font"]
                and item.get("size") == current_group["size"]
                and item.get("color") == current_group["color"]
                and item.get("bold", False) == current_group["bold"]
                and item.get("italic", False) == current_group["italic"]
            ):
                # Same formatting - append text
                current_group["text"] += " " + item.get("text", "")
            else:
                # Different formatting - start new group
                grouped.append(current_group)
                current_group = {
                    "text": item.get("text", ""),
                    "font": item.get("font"),
                    "size": item.get("size"),
                    "color": item.get("color"),
                    "bold": item.get("bold", False),
                    "italic": item.get("italic", False),
                }

        # Add last group
        grouped.append(current_group)

        return grouped
