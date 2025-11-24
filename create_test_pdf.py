"""
Test script to demonstrate PDF processing implementation
Creates a minimal test PDF to verify sections 1.1-2.5
"""


def create_minimal_pdf():
    """
    Create a minimal valid PDF for testing
    This PDF contains basic structure elements covered in sections 1-2.5
    """

    # Minimal PDF structure with FlateDecode compression
    pdf_content = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000308 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
401
%%EOF"""

    return pdf_content


def create_compressed_pdf():
    """
    Create a PDF with compressed stream (FlateDecode)
    Tests section 2.5 compression handling
    """
    import zlib

    # Compress the content stream
    content = b"BT\n/F1 12 Tf\n100 700 Td\n(Hello World from Compressed PDF!) Tj\nET\n"
    compressed = zlib.compress(content)

    # Build PDF with compressed stream
    pdf_parts = [
        b"%PDF-1.7\n",
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>\nendobj\n",
        b"5 0 obj\n<< /Length "
        + str(len(compressed)).encode()
        + b" /Filter /FlateDecode >>\nstream\n",
        compressed,
        b"\nendstream\nendobj\n",
        b"xref\n0 6\n",
        b"0000000000 65535 f \n",
        b"0000000009 00000 n \n",
        b"0000000058 00000 n \n",
        b"0000000115 00000 n \n",
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF",
    ]

    return b"".join(pdf_parts)


def main():
    """Create test PDF files"""

    print("Creating test PDF files...")

    # Create minimal PDF
    minimal_pdf = create_minimal_pdf()
    with open("test_minimal.pdf", "wb") as f:
        f.write(minimal_pdf)
    print("✓ Created test_minimal.pdf (uncompressed)")

    # Create compressed PDF
    compressed_pdf = create_compressed_pdf()
    with open("test_compressed.pdf", "wb") as f:
        f.write(compressed_pdf)
    print("✓ Created test_compressed.pdf (with FlateDecode)")

    print("\nTest files created successfully!")
    print("\nTo test the implementation, run:")
    print("  python main.py test_minimal.pdf")
    print("  python main.py test_compressed.pdf")


if __name__ == "__main__":
    main()
