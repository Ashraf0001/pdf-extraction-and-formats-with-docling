import streamlit as st
import pandas as pd
import json
import markdown
import io
import base64
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="PDF to Markdown/JSON/CSV Converter",
    page_icon="📄",
    layout="wide"
)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF using multiple methods for better results."""
    try:
        # Try pdfplumber first (better for complex layouts)
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text
        
        # Fallback to PyPDF2
        pdf_file.seek(0)  # Reset file pointer
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def process_pdf_to_markdown(text: str) -> str:
    """Convert extracted text to markdown format."""
    if not text.strip():
        return "# No text extracted from PDF"
    
    # Simple markdown conversion
    lines = text.split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Simple heuristics for markdown formatting
        if line.isupper() and len(line) > 3:
            markdown_lines.append(f"## {line}")
        elif line.endswith(':') and len(line) < 50:
            markdown_lines.append(f"### {line}")
        else:
            markdown_lines.append(line)
    
    return '\n\n'.join(markdown_lines)

def process_pdf_to_json(text: str, filename: str) -> Dict[str, Any]:
    """Convert extracted text to JSON format."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return {
        "filename": filename,
        "total_lines": len(lines),
        "content": lines,
        "summary": {
            "word_count": len(text.split()),
            "character_count": len(text),
            "line_count": len(lines)
        }
    }

def process_pdf_to_csv(text: str) -> pd.DataFrame:
    """Convert extracted text to CSV format."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Create a DataFrame with line numbers and content
    df = pd.DataFrame({
        'Line_Number': range(1, len(lines) + 1),
        'Content': lines,
        'Word_Count': [len(line.split()) for line in lines],
        'Character_Count': [len(line) for line in lines]
    })
    
    return df

def get_download_link(data, filename: str, file_type: str):
    """Generate download link for files."""
    if file_type == "csv":
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV file</a>'
    elif file_type == "json":
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">Download JSON file</a>'
    elif file_type == "markdown":
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}.md">Download Markdown file</a>'
    
    return href

def main():
    st.title("📄 PDF to Markdown/JSON/CSV Converter")
    st.markdown("Upload your PDF files and convert them to different formats!")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose PDF file(s)",
        type=['pdf'],
        accept_multiple_files=True,
        help="You can upload multiple PDF files at once"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} file(s)")
        
        # Output format selection
        output_format = st.selectbox(
            "Select output format:",
            ["Markdown", "JSON", "CSV"],
            help="Choose the format you want to download"
        )
        
        # Process button
        if st.button("Process PDF(s)", type="primary"):
            with st.spinner("Processing PDF(s)..."):
                for uploaded_file in uploaded_files:
                    st.subheader(f"Processing: {uploaded_file.name}")
                    
                    # Extract text from PDF
                    text = extract_text_from_pdf(uploaded_file)
                    
                    if text.strip():
                        # Process based on selected format
                        if output_format == "Markdown":
                            processed_data = process_pdf_to_markdown(text)
                            st.text_area("Preview:", processed_data, height=200)
                            
                            # Download link
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "markdown"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        elif output_format == "JSON":
                            processed_data = process_pdf_to_json(text, uploaded_file.name)
                            st.json(processed_data)
                            
                            # Download link
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "json"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        elif output_format == "CSV":
                            processed_data = process_pdf_to_csv(text)
                            st.dataframe(processed_data)
                            
                            # Download link
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "csv"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                    else:
                        st.error("No text could be extracted from this PDF.")
                    
                    st.divider()
    else:
        st.info("👆 Please upload PDF file(s) to get started!")
        
        # Add some helpful information
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            1. **Upload PDF(s)**: Click the upload button and select one or more PDF files
            2. **Choose Format**: Select your desired output format (Markdown, JSON, or CSV)
            3. **Process**: Click the 'Process PDF(s)' button
            4. **Download**: Use the download links to save your converted files
            
            **Supported Formats:**
            - **Markdown**: Clean, formatted text with basic structure
            - **JSON**: Structured data with metadata and content
            - **CSV**: Tabular format with line-by-line breakdown
            """)

if __name__ == "__main__":
    main() 