import streamlit as st
import pandas as pd
import json
import markdown
import io
import base64
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="PDF to Markdown/JSON/CSV Converter",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better markdown styling
st.markdown("""
<style>
    .markdown-text-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .markdown-text-container h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    
    .markdown-text-container h2 {
        color: #34495e;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 5px;
    }
    
    .markdown-text-container h3 {
        color: #7f8c8d;
    }
    
    .markdown-text-container table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
    }
    
    .markdown-text-container th {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: left;
        border: 1px solid #2980b9;
    }
    
    .markdown-text-container td {
        padding: 8px 12px;
        border: 1px solid #ddd;
    }
    
    .markdown-text-container tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    .markdown-text-container tr:hover {
        background-color: #e8f4fd;
    }
    
    .markdown-text-container ul, .markdown-text-container ol {
        padding-left: 20px;
    }
    
    .markdown-text-container li {
        margin: 5px 0;
    }
    
    .markdown-text-container blockquote {
        border-left: 4px solid #3498db;
        margin: 0;
        padding-left: 20px;
        color: #7f8c8d;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

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

def extract_tables_from_pdf(pdf_file) -> List[pd.DataFrame]:
    """Extract tables from PDF using pdfplumber."""
    tables = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table_num, table in enumerate(page_tables):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df['Page'] = page_num + 1
                        df['Table'] = table_num + 1
                        tables.append(df)
    except Exception as e:
        st.warning(f"Table extraction failed: {str(e)}")
    
    return tables

def process_pdf_to_markdown(text: str, tables: Optional[List[pd.DataFrame]] = None) -> str:
    """Convert extracted text to markdown format with enhanced formatting and table support."""
    if not text.strip() and not tables:
        return "# No text extracted from PDF"
    
    markdown_parts = []
    
    # Process text with enhanced formatting
    if text.strip():
        lines = text.split('\n')
        markdown_lines = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                # Process accumulated paragraph
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")  # Add spacing
                    current_paragraph = []
                continue
            
            # Enhanced header detection
            if line.isupper() and len(line) > 3 and len(line) < 100:
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add header with better formatting
                markdown_lines.append(f"## {line.title()}")
                markdown_lines.append("")
                
            elif line.endswith(':') and len(line) < 80 and not line.startswith('http'):
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add subheader
                markdown_lines.append(f"### {line}")
                markdown_lines.append("")
                
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add bullet point
                markdown_lines.append(f"- {line[1:].strip()}")
                
            elif line.isdigit() and len(line) <= 3:
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add numbered list item
                markdown_lines.append(f"{line}.")
                
            elif line.startswith('**') and line.endswith('**'):
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add bold text as emphasis
                markdown_lines.append(f"**{line[2:-2]}**")
                
            elif line.startswith('_') and line.endswith('_'):
                # Process any accumulated paragraph first
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph)
                    if len(paragraph_text) > 0:
                        markdown_lines.append(paragraph_text)
                        markdown_lines.append("")
                    current_paragraph = []
                
                # Add italic text
                markdown_lines.append(f"*{line[1:-1]}*")
                
            else:
                # Add to current paragraph
                current_paragraph.append(line)
        
        # Process any remaining paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            if len(paragraph_text) > 0:
                markdown_lines.append(paragraph_text)
        
        # Clean up and format
        formatted_lines = []
        for line in markdown_lines:
            if line.strip():
                # Clean up extra spaces
                cleaned_line = ' '.join(line.split())
                formatted_lines.append(cleaned_line)
            else:
                formatted_lines.append("")
        
        markdown_parts.append('\n'.join(formatted_lines))
    
    # Process tables with enhanced formatting
    if tables:
        markdown_parts.append("\n---")
        markdown_parts.append("\n## 📊 Tables")
        markdown_parts.append("")
        
        for i, table in enumerate(tables):
            markdown_parts.append(f"### Table {i+1} (Page {table['Page'].iloc[0]})")
            markdown_parts.append("")
            
            # Create enhanced table with better formatting
            table_df = table.drop(['Page', 'Table'], axis=1)
            
            # Add table header
            headers = list(table_df.columns)
            markdown_parts.append("| " + " | ".join(headers) + " |")
            markdown_parts.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            # Add table rows
            for _, row in table_df.iterrows():
                row_values = [str(val) if pd.notna(val) else "" for val in row.values]
                markdown_parts.append("| " + " | ".join(row_values) + " |")
            
            markdown_parts.append("")
            markdown_parts.append(f"*Table {i+1} contains {len(table_df)} rows and {len(headers)} columns*")
            markdown_parts.append("")
    
    # Add document summary
    if text.strip():
        word_count = len(text.split())
        char_count = len(text)
        line_count = len([line for line in text.split('\n') if line.strip()])
        
        markdown_parts.append("---")
        markdown_parts.append("## 📋 Document Summary")
        markdown_parts.append("")
        markdown_parts.append(f"- **Word Count**: {word_count:,}")
        markdown_parts.append(f"- **Character Count**: {char_count:,}")
        markdown_parts.append(f"- **Line Count**: {line_count:,}")
        if tables:
            markdown_parts.append(f"- **Tables Found**: {len(tables)}")
    
    return '\n'.join(markdown_parts)

def process_pdf_to_json(text: str, filename: str, tables: Optional[List[pd.DataFrame]] = None) -> Dict[str, Any]:
    """Convert extracted text to JSON format with table support."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    result = {
        "filename": filename,
        "total_lines": len(lines),
        "content": lines,
        "summary": {
            "word_count": len(text.split()),
            "character_count": len(text),
            "line_count": len(lines),
            "table_count": len(tables) if tables else 0
        }
    }
    
    # Add tables if available
    if tables:
        result["tables"] = []
        for i, table in enumerate(tables):
            table_data = {
                "table_number": i + 1,
                "page": int(table['Page'].iloc[0]),
                "rows": len(table),
                "columns": len(table.columns) - 2,  # Exclude Page and Table columns
                "data": table.drop(['Page', 'Table'], axis=1).to_dict('records')
            }
            result["tables"].append(table_data)
    
    return result

def process_pdf_to_csv(text: str, tables: Optional[List[pd.DataFrame]] = None) -> Dict[str, pd.DataFrame]:
    """Convert extracted text to CSV format with table support."""
    result = {}
    
    # Text content
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        text_df = pd.DataFrame({
            'Line_Number': range(1, len(lines) + 1),
            'Content': lines,
            'Word_Count': [len(line.split()) for line in lines],
            'Character_Count': [len(line) for line in lines]
        })
        result['text_content'] = text_df
    
    # Tables
    if tables:
        for i, table in enumerate(tables):
            result[f'table_{i+1}'] = table
    
    return result

def get_download_link(data, filename: str, file_type: str):
    """Generate download link for files."""
    if file_type == "csv":
        if isinstance(data, dict):
            # Multiple CSV files (text + tables)
            csv_data = data.get('text_content', pd.DataFrame())
            if not csv_data.empty:
                csv = csv_data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}_text.csv">Download Text CSV</a>'
                
                # Add table downloads
                for key, table_df in data.items():
                    if key != 'text_content' and isinstance(table_df, pd.DataFrame):
                        csv = table_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href += f'<br><a href="data:file/csv;base64,{b64}" download="{filename}_{key}.csv">Download {key.replace("_", " ").title()} CSV</a>'
                return href
        else:
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
    st.markdown("Upload your PDF files and convert them to different formats with enhanced processing!")
    
    st.success("✅ Using enhanced PDF processing with table extraction")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose PDF file(s)",
        type=['pdf'],
        accept_multiple_files=True,
        help="You can upload multiple PDF files at once"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} file(s)")
        
        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            extract_tables = st.checkbox("Extract tables", value=True, help="Extract tables from PDFs")
        with col2:
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
                    
                    # Extract tables if requested
                    tables = None
                    if extract_tables:
                        tables = extract_tables_from_pdf(uploaded_file)
                        if tables:
                            st.success(f"Found {len(tables)} table(s)")
                    
                    if text.strip() or tables:
                        # Process based on selected format
                        if output_format == "Markdown":
                            processed_data = process_pdf_to_markdown(text, tables)
                            
                            # Create tabs for different views
                            tab1, tab2 = st.tabs(["📄 Rendered Preview", "📝 Raw Markdown"])
                            
                            with tab1:
                                # Rendered markdown with custom styling
                                st.markdown(f"""
                                <div class="markdown-text-container">
                                {markdown.markdown(processed_data)}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with tab2:
                                # Raw markdown text
                                st.text_area("Raw Markdown:", processed_data, height=400)
                            
                            # Download link
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "markdown"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        elif output_format == "JSON":
                            processed_data = process_pdf_to_json(text, uploaded_file.name, tables)
                            st.json(processed_data)
                            
                            # Download link
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "json"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        elif output_format == "CSV":
                            processed_data = process_pdf_to_csv(text, tables)
                            
                            # Display text content
                            if 'text_content' in processed_data:
                                st.subheader("Text Content")
                                st.dataframe(processed_data['text_content'])
                            
                            # Display tables
                            for key, table_df in processed_data.items():
                                if key != 'text_content':
                                    st.subheader(f"Table {key.replace('_', ' ').title()}")
                                    st.dataframe(table_df)
                            
                            # Download links
                            download_link = get_download_link(
                                processed_data, 
                                uploaded_file.name.replace('.pdf', ''), 
                                "csv"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                    else:
                        st.error("No text or tables could be extracted from this PDF.")
                    
                    st.divider()
    else:
        st.info("👆 Please upload PDF file(s) to get started!")
        
        # Add some helpful information
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            1. **Upload PDF(s)**: Click the upload button and select one or more PDF files
            2. **Choose Options**: Select whether to extract tables and your desired output format
            3. **Process**: Click the 'Process PDF(s)' button
            4. **Download**: Use the download links to save your converted files
            
            **Features:**
            - **Table Extraction**: Automatically detect and extract tables from PDFs
            - **Multiple Outputs**: Get separate files for text and tables in CSV format
            - **Robust Processing**: Uses multiple PDF parsing libraries for better results
            
            **Supported Formats:**
            - **Markdown**: Clean, formatted text with table support
            - **JSON**: Structured data with metadata, content, and tables
            - **CSV**: Multiple files for text content and individual tables
            """)

if __name__ == "__main__":
    main() 