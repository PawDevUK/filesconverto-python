"""
DOCX Generator Module
Implements section 10 from convertion_process.md
"""

import zipfile
import io
from typing import List, Dict, Any
from datetime import datetime


class DOCXGenerator:
    """Handles DOCX file generation"""

    @staticmethod
    def create_content_types_xml() -> str:
        """
        Create [Content_Types].xml
        Section 10.2: Content Types XML

        Returns:
            str: Content types XML content
        """
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" 
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" 
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/fontTable.xml" 
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/docProps/core.xml" 
    ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" 
    ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    @staticmethod
    def create_rels_xml() -> str:
        """
        Create _rels/.rels
        Section 10.3: Relationships XML

        Returns:
            str: Main relationships XML content
        """
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" 
    Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" 
    Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" 
    Target="docProps/app.xml"/>
</Relationships>"""

    @staticmethod
    def create_document_rels_xml() -> str:
        """
        Create word/_rels/document.xml.rels
        Section 10.3: Relationships XML

        Returns:
            str: Document relationships XML content
        """
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" 
    Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" 
    Target="fontTable.xml"/>
</Relationships>"""

    @staticmethod
    def create_styles_xml() -> str:
        """
        Create word/styles.xml
        Section 10.4: Styles XML

        Returns:
            str: Styles XML content
        """
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
        <w:sz w:val="22"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
</w:styles>"""

    @staticmethod
    def create_font_table_xml(fonts: List[str]) -> str:
        """
        Create word/fontTable.xml
        Section 10.5: Font Table XML

        Args:
            fonts: List of font names used in document

        Returns:
            str: Font table XML content
        """
        xml_parts = []
        xml_parts.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        xml_parts.append(
            '<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        )

        # Add each unique font
        unique_fonts = set(fonts) if fonts else {"Calibri"}
        for font_name in sorted(unique_fonts):
            xml_parts.append(f'  <w:font w:name="{font_name}">')
            xml_parts.append(f'    <w:panose1 w:val="00000000000000000000"/>')
            xml_parts.append(f'    <w:charset w:val="00"/>')
            xml_parts.append(f'    <w:family w:val="auto"/>')
            xml_parts.append(f'    <w:pitch w:val="variable"/>')
            xml_parts.append(f"  </w:font>")

        xml_parts.append("</w:fonts>")
        return "\n".join(xml_parts)

    @staticmethod
    def create_core_props_xml() -> str:
        """
        Create docProps/core.xml

        Returns:
            str: Core properties XML content
        """
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:dcterms="http://purl.org/dc/terms/" 
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>PDF Converter</dc:creator>
  <cp:lastModifiedBy>PDF Converter</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""

    @staticmethod
    def create_app_props_xml() -> str:
        """
        Create docProps/app.xml

        Returns:
            str: Application properties XML content
        """
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>PDF Converter</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <Company></Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>1.0</AppVersion>
</Properties>"""

    @staticmethod
    def escape_xml(text: str) -> str:
        """
        Escape XML special characters

        Args:
            text: Text to escape

        Returns:
            str: Escaped text
        """
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        return text

    @staticmethod
    def create_document_xml(content_items: List[Dict[str, Any]]) -> str:
        """
        Create word/document.xml content
        Section 10.1: DOCX XML Generation

        Args:
            content_items: List of content items with text and formatting

        Returns:
            str: Document XML content
        """
        xml_parts = []

        # XML header
        xml_parts.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        xml_parts.append(
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        )
        xml_parts.append("  <w:body>")

        # Process content items (paragraphs with formatting)
        for item in content_items:
            text = item.get("text", "")
            if not text.strip():
                continue

            xml_parts.append("    <w:p>")  # Paragraph

            # Paragraph properties
            xml_parts.append("      <w:pPr>")
            xml_parts.append('        <w:jc w:val="left"/>')  # Justification
            xml_parts.append("      </w:pPr>")

            # Run (text with formatting)
            xml_parts.append("      <w:r>")
            xml_parts.append("        <w:rPr>")  # Run properties

            # Font
            if "font" in item and item["font"]:
                font_name = DOCXGenerator.escape_xml(str(item["font"]))
                xml_parts.append(
                    f'          <w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}"/>'
                )

            # Font size (in half-points)
            if "size" in item and item["size"]:
                try:
                    size_half_points = int(float(item["size"]) * 2)
                    xml_parts.append(f'          <w:sz w:val="{size_half_points}"/>')
                    xml_parts.append(f'          <w:szCs w:val="{size_half_points}"/>')
                except (ValueError, TypeError):
                    pass

            # Color
            if "color" in item and item["color"]:
                color_hex = item["color"]
                if isinstance(color_hex, str):
                    xml_parts.append(f'          <w:color w:val="{color_hex}"/>')

            # Bold
            if item.get("bold", False):
                xml_parts.append("          <w:b/>")

            # Italic
            if item.get("italic", False):
                xml_parts.append("          <w:i/>")

            xml_parts.append("        </w:rPr>")

            # Text content
            escaped_text = DOCXGenerator.escape_xml(text)
            xml_parts.append(f'        <w:t xml:space="preserve">{escaped_text}</w:t>')

            xml_parts.append("      </w:r>")
            xml_parts.append("    </w:p>")

        # If no content, add empty paragraph
        if not content_items:
            xml_parts.append("    <w:p/>")

        xml_parts.append("  </w:body>")
        xml_parts.append("</w:document>")

        return "\n".join(xml_parts)

    @staticmethod
    def create_docx_file(
        content_items: List[Dict[str, Any]], output_path: str, fonts: List[str] = None
    ) -> None:
        """
        Create complete DOCX file
        Section 10.6: Complete DOCX Assembly

        Args:
            content_items: List of content items with text and formatting
            output_path: Path to output DOCX file
            fonts: List of fonts used (optional, will be extracted from content_items)
        """
        # Extract unique fonts if not provided
        if fonts is None:
            fonts = []
            for item in content_items:
                font = item.get("font")
                if font and font not in fonts:
                    fonts.append(font)

        if not fonts:
            fonts = ["Calibri"]

        # Create ZIP archive (DOCX is a ZIP file)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as docx:
            # Add all required files
            docx.writestr(
                "[Content_Types].xml", DOCXGenerator.create_content_types_xml()
            )
            docx.writestr("_rels/.rels", DOCXGenerator.create_rels_xml())
            docx.writestr(
                "word/document.xml", DOCXGenerator.create_document_xml(content_items)
            )
            docx.writestr(
                "word/_rels/document.xml.rels", DOCXGenerator.create_document_rels_xml()
            )
            docx.writestr("word/styles.xml", DOCXGenerator.create_styles_xml())
            docx.writestr(
                "word/fontTable.xml", DOCXGenerator.create_font_table_xml(fonts)
            )

            # Add document properties
            docx.writestr("docProps/core.xml", DOCXGenerator.create_core_props_xml())
            docx.writestr("docProps/app.xml", DOCXGenerator.create_app_props_xml())

    @staticmethod
    def create_docx_from_text(text: str, output_path: str) -> None:
        """
        Create simple DOCX from plain text

        Args:
            text: Plain text content
            output_path: Path to output DOCX file
        """
        content_items = [{"text": text, "font": "Calibri", "size": 11}]
        DOCXGenerator.create_docx_file(content_items, output_path)
