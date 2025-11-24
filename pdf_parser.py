"""
PDF Structure Parsing Module
Implements sections 2.1-2.4 from convertion_process.md
"""

import re
from typing import Dict, List, Tuple, Any


class PDFParser:
    """Handles PDF file structure parsing"""

    @staticmethod
    def extract_pdf_version(data: bytes) -> str:
        """
        Extract PDF version from header
        Section 2.2: PDF Header

        Args:
            data: Binary PDF content

        Returns:
            str: PDF version (e.g., "1.7")
        """
        header_line = data.split(b"\n")[0]
        # Example: b'%PDF-1.7'
        version = header_line.decode("latin-1").split("-")[1]
        return version

    @staticmethod
    def tokenize_pdf(data: bytes) -> List[bytes]:
        """
        Split PDF content into tokens
        Section 5.1: Tokenization

        Args:
            data: Binary PDF content

        Returns:
            List[bytes]: List of tokens
        """
        delimiters = b" \t\r\n\x00"

        tokens = []
        current_token = b""
        in_string = False

        for byte in data:
            byte_char = bytes([byte])

            if byte_char == b"(" and not in_string:
                in_string = True
                current_token += byte_char
            elif byte_char == b")" and in_string:
                in_string = False
                current_token += byte_char
                tokens.append(current_token)
                current_token = b""
            elif byte_char in delimiters and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = b""
            else:
                current_token += byte_char

        if current_token:
            tokens.append(current_token)

        return tokens

    @staticmethod
    def extract_objects(data: bytes) -> Dict[Tuple[int, int], bytes]:
        """
        Extract all objects from PDF
        Section 2.3: PDF Objects & 5.2: Object Extraction

        Args:
            data: Binary PDF content

        Returns:
            Dict: Dictionary mapping (obj_num, gen_num) to object content
        """
        objects = {}

        # Pattern: "N M obj ... endobj"
        obj_pattern = rb"(\d+)\s+(\d+)\s+obj(.*?)endobj"

        matches = re.finditer(obj_pattern, data, re.DOTALL)

        for match in matches:
            obj_num = int(match.group(1))
            gen_num = int(match.group(2))
            obj_content = match.group(3)

            objects[(obj_num, gen_num)] = obj_content

        return objects

    @staticmethod
    def parse_xref(data: bytes) -> Dict[int, Tuple[int, int]]:
        """
        Parse cross-reference table
        Section 5.3: Cross-Reference Table Parsing

        Args:
            data: Binary PDF content

        Returns:
            Dict: Dictionary mapping object index to (offset, generation)
        """
        xref_start = data.rfind(b"startxref")
        if xref_start == -1:
            raise ValueError("No xref table found")

        # Get xref offset
        offset_data = data[xref_start + 9 :].split(b"\n")[1]
        xref_offset = int(offset_data.strip())

        # Parse xref entries
        xref_data = data[xref_offset:]
        entries = {}

        # Format: "offset generation_num n/f"
        # n = in use, f = free
        lines = xref_data.split(b"\n")
        obj_index = 0

        for line in lines[2:]:  # Skip "xref" and subsection header
            if line.strip() == b"trailer":
                break
            if len(line.strip()) == 20:  # xref entry is 20 bytes
                offset = int(line[0:10])
                gen = int(line[11:16])
                flag = line[17:18]
                if flag == b"n":
                    entries[obj_index] = (offset, gen)
                obj_index += 1

        return entries

    @staticmethod
    def parse_pdf_dictionary(dict_bytes: bytes) -> Dict[str, Any]:
        """
        Parse PDF dictionary: << /Key Value /Key2 Value2 >>
        Section 5.4: Dictionary Parsing

        Args:
            dict_bytes: Binary dictionary content

        Returns:
            Dict: Parsed dictionary
        """
        dict_content = {}

        # Remove << and >>
        content = dict_bytes.strip()
        if content.startswith(b"<<"):
            content = content[2:]
        if content.endswith(b">>"):
            content = content[:-2]

        tokens = content.split()
        i = 0
        while i < len(tokens):
            if tokens[i].startswith(b"/"):
                # This is a key
                key = tokens[i][1:].decode("latin-1")  # Remove '/'
                if i + 1 < len(tokens):
                    value = tokens[i + 1]
                    # Try to decode value if it's a name
                    if value.startswith(b"/"):
                        value = value[1:].decode("latin-1")
                    dict_content[key] = value
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        return dict_content

    @staticmethod
    def find_content_streams(
        objects: Dict[Tuple[int, int], bytes],
    ) -> List[Dict[str, Any]]:
        """
        Find all content streams in PDF objects
        Section 2.4: PDF Content Streams & 6.1: Locating Content Streams

        Args:
            objects: Dictionary of PDF objects

        Returns:
            List[Dict]: List of content stream information
        """
        content_streams = []

        for (obj_num, gen_num), obj_content in objects.items():
            # Look for stream objects
            if b"stream" in obj_content and b"endstream" in obj_content:
                # Extract dictionary and stream
                dict_end = obj_content.find(b"stream")
                dictionary = obj_content[:dict_end]

                # Find actual stream start (after 'stream' keyword and newline)
                stream_keyword_pos = obj_content.find(b"stream")
                stream_start = stream_keyword_pos + 6
                # Skip whitespace/newlines after 'stream'
                while (
                    stream_start < len(obj_content)
                    and obj_content[stream_start : stream_start + 1] in b"\r\n "
                ):
                    stream_start += 1

                stream_end = obj_content.find(b"endstream")
                stream_data = obj_content[stream_start:stream_end]

                # Parse dictionary to check for filters
                dict_obj = PDFParser.parse_pdf_dictionary(dictionary)

                content_streams.append(
                    {
                        "obj_num": obj_num,
                        "gen_num": gen_num,
                        "dictionary": dict_obj,
                        "stream": stream_data,
                    }
                )

        return content_streams

    @staticmethod
    def parse_pdf_structure(data: bytes) -> Dict[str, Any]:
        """
        Complete PDF structure parsing
        Combines sections 2.1-2.4

        Args:
            data: Binary PDF content

        Returns:
            Dict: Complete PDF structure information
        """
        # Extract version
        version = PDFParser.extract_pdf_version(data)

        # Extract objects
        objects = PDFParser.extract_objects(data)

        # Parse xref table
        try:
            xref = PDFParser.parse_xref(data)
        except ValueError:
            xref = {}

        # Find content streams
        content_streams = PDFParser.find_content_streams(objects)

        return {
            "version": version,
            "objects": objects,
            "xref": xref,
            "content_streams": content_streams,
            "total_objects": len(objects),
            "total_streams": len(content_streams),
        }
