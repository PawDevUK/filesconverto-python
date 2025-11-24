"""
PDF Compression Module
Implements section 2.5 from convertion_process.md
"""

import zlib
from typing import Optional, Dict, Any


class PDFCompression:
    """Handles PDF stream compression and decompression"""

    # Supported compression filters
    FLATE_DECODE = "FlateDecode"
    LZW_DECODE = "LZWDecode"
    ASCII85_DECODE = "ASCII85Decode"
    DCT_DECODE = "DCTDecode"
    CCITT_FAX_DECODE = "CCITTFaxDecode"

    @staticmethod
    def decompress_flate(compressed_data: bytes) -> bytes:
        """
        Decompress FlateDecode stream
        Section 2.5: PDF Compression - FlateDecode

        FlateDecode uses ZLIB/Deflate compression (most common in PDFs)

        Args:
            compressed_data: Compressed binary data

        Returns:
            bytes: Decompressed data

        Raises:
            ValueError: If decompression fails
        """
        try:
            # Try standard decompression
            return zlib.decompress(compressed_data)
        except zlib.error:
            try:
                # Try with different window size (-15 for raw deflate)
                return zlib.decompress(compressed_data, -15)
            except zlib.error as e:
                raise ValueError(f"FlateDecode decompression failed: {e}")

    @staticmethod
    def decompress_stream(stream_data: bytes, filter_type: Any) -> bytes:
        """
        Decompress stream based on filter type
        Section 2.5: PDF Compression

        Args:
            stream_data: Compressed stream data
            filter_type: Filter type (can be bytes or string)

        Returns:
            bytes: Decompressed data

        Raises:
            NotImplementedError: For unsupported compression types
        """
        # Convert filter type to string if it's bytes
        if isinstance(filter_type, bytes):
            filter_str = filter_type.decode("latin-1")
            # Remove leading '/' if present
            if filter_str.startswith("/"):
                filter_str = filter_str[1:]
        else:
            filter_str = str(filter_type)
            if filter_str.startswith("/"):
                filter_str = filter_str[1:]

        # Handle FlateDecode (ZLIB/Deflate compression - most common)
        if filter_str == PDFCompression.FLATE_DECODE:
            return PDFCompression.decompress_flate(stream_data)

        # Handle LZWDecode (LZW compression)
        elif filter_str == PDFCompression.LZW_DECODE:
            raise NotImplementedError(
                "LZWDecode compression is not implemented in vanilla Python"
            )

        # Handle ASCII85Decode (ASCII encoding)
        elif filter_str == PDFCompression.ASCII85_DECODE:
            raise NotImplementedError(
                "ASCII85Decode compression is not implemented in vanilla Python"
            )

        # Handle DCTDecode (JPEG compression for images)
        elif filter_str == PDFCompression.DCT_DECODE:
            # DCT is JPEG - data is already in usable format, no decompression needed
            return stream_data

        # Handle CCITTFaxDecode (Fax compression)
        elif filter_str == PDFCompression.CCITT_FAX_DECODE:
            raise NotImplementedError(
                "CCITTFaxDecode compression is not implemented in vanilla Python"
            )

        else:
            # Unknown filter or no filter
            return stream_data

    @staticmethod
    def process_content_stream(stream_info: Dict[str, Any]) -> Optional[bytes]:
        """
        Process and decompress a content stream
        Combines sections 2.4 and 2.5

        Args:
            stream_info: Dictionary containing stream data and metadata
                        Expected keys: 'stream', 'dictionary'

        Returns:
            Optional[bytes]: Decompressed stream data, or None if processing fails
        """
        stream_data = stream_info.get("stream")
        dictionary = stream_info.get("dictionary", {})

        if not stream_data:
            return None

        # Check if stream has a filter
        filter_type = dictionary.get("Filter")

        if filter_type:
            try:
                decompressed = PDFCompression.decompress_stream(
                    stream_data, filter_type
                )
                return decompressed
            except (NotImplementedError, ValueError) as e:
                # Return original data if decompression fails
                print(f"Warning: Could not decompress stream: {e}")
                return stream_data
        else:
            # No filter - return as is
            return stream_data

    @staticmethod
    def process_all_streams(content_streams: list) -> Dict[int, bytes]:
        """
        Process and decompress all content streams

        Args:
            content_streams: List of stream information dictionaries

        Returns:
            Dict: Dictionary mapping object numbers to decompressed stream data
        """
        processed_streams = {}

        for stream_info in content_streams:
            obj_num = stream_info.get("obj_num")
            if obj_num is not None:
                decompressed = PDFCompression.process_content_stream(stream_info)
                if decompressed:
                    processed_streams[obj_num] = decompressed

        return processed_streams

    @staticmethod
    def get_compression_info(content_streams: list) -> Dict[str, Any]:
        """
        Analyze compression methods used in PDF

        Args:
            content_streams: List of stream information dictionaries

        Returns:
            Dict: Statistics about compression methods used
        """
        filter_counts = {}
        total_streams = len(content_streams)
        compressed_streams = 0

        for stream_info in content_streams:
            dictionary = stream_info.get("dictionary", {})
            filter_type = dictionary.get("Filter")

            if filter_type:
                compressed_streams += 1
                # Convert to string for counting
                if isinstance(filter_type, bytes):
                    filter_str = filter_type.decode("latin-1")
                else:
                    filter_str = str(filter_type)

                filter_counts[filter_str] = filter_counts.get(filter_str, 0) + 1

        return {
            "total_streams": total_streams,
            "compressed_streams": compressed_streams,
            "uncompressed_streams": total_streams - compressed_streams,
            "compression_methods": filter_counts,
        }
