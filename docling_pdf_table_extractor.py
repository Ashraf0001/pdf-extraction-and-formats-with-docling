import sys
from docling.document_converter import DocumentConverter
from docling.datamodel.document import DocumentConversionInput
import json
import os
from pathlib import Path

def main(pdf_path):
    # Prepare Docling input
    doc_input = DocumentConversionInput.from_paths([Path(pdf_path)])
    converter = DocumentConverter()
    # convert() returns an iterable of ConvertedDocument
    for result in converter.convert(doc_input):
        # Export to Markdown
        markdown = result.render_as_markdown()
        md_out = os.path.splitext(pdf_path)[0] + "_docling.md"
        with open(md_out, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Markdown exported to: {md_out}")

        # Export to JSON
        json_data = result.render_as_dict()
        json_out = os.path.splitext(pdf_path)[0] + "_docling.json"
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSON exported to: {json_out}")
        break  # Only process the first document

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python docling_pdf_table_extractor.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    main(pdf_path) 