"""
File Upload and Reading Module
Implements sections 1.1-1.3 from convertion_process.md
"""


class FileHandler:
    """Handles file upload, reading, and validation"""

    @staticmethod
    def read_binary_file(file_path):
        """
        Read binary file data
        Section 1.1: File Upload Mechanism

        Args:
            file_path: Path to the file to read

        Returns:
            bytes: Binary file content
        """
        with open(file_path, "rb") as file:
            pdf_binary_data = file.read()
        return pdf_binary_data

    @staticmethod
    def get_file_info(pdf_binary_data):
        """
        Get binary data structure information
        Section 1.2: Binary Data Structure

        Args:
            pdf_binary_data: Binary content of PDF file

        Returns:
            dict: Information about the file
        """
        first_bytes = pdf_binary_data[0:8]
        file_size = len(pdf_binary_data)

        return {
            "first_bytes": first_bytes,
            "file_size": file_size,
            "header": first_bytes.decode("latin-1", errors="ignore"),
        }

    @staticmethod
    def validate_pdf(data):
        """
        Validate if file is a valid PDF
        Section 1.3: File Validation

        Args:
            data: Binary file content

        Returns:
            bool: True if valid PDF, False otherwise
        """
        # Check PDF header
        if not data.startswith(b"%PDF-"):
            return False

        # Check EOF marker
        if b"%%EOF" not in data[-1024:]:
            return False

        return True

    @staticmethod
    def upload_and_validate(file_path):
        """
        Complete upload and validation process
        Combines sections 1.1-1.3

        Args:
            file_path: Path to PDF file

        Returns:
            tuple: (binary_data, is_valid, info)
        """
        # Read file
        binary_data = FileHandler.read_binary_file(file_path)

        # Validate
        is_valid = FileHandler.validate_pdf(binary_data)

        # Get info
        info = FileHandler.get_file_info(binary_data)

        return binary_data, is_valid, info
