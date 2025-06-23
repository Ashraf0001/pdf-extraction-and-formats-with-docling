import streamlit as st
import pandas as pd
import json
import os
import tempfile
from pathlib import Path
import base64

# Page configuration
st.set_page_config(
    page_title="Advanced PDF Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .method-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def extract_with_camelot(pdf_path):
    """Extract tables using Camelot."""
    try:
        import camelot.io as camelot
        st.write("Trying Camelot...")
        
        # Try different table detection methods
        tables = []
        
        # Method 1: Lattice (for tables with borders)
        try:
            with st.spinner("Camelot Lattice method..."):
                lattice_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
                tables.extend(lattice_tables)
                st.write(f"  Lattice method found {len(lattice_tables)} tables")
        except Exception as e:
            st.write(f"  Lattice method failed: {e}")
        
        # Method 2: Stream (for tables without borders)
        try:
            with st.spinner("Camelot Stream method..."):
                stream_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
                tables.extend(stream_tables)
                st.write(f"  Stream method found {len(stream_tables)} tables")
        except Exception as e:
            st.write(f"  Stream method failed: {e}")
        
        if tables:
            st.write(f"  Total Camelot tables: {len(tables)}")
            return tables
        else:
            st.write("  Camelot found no tables")
            return []
            
    except ImportError:
        st.write("Camelot not available")
        return []
    except Exception as e:
        st.write(f"Camelot error: {e}")
        return []

def extract_with_pdfplumber(pdf_path):
    """Extract tables and text using pdfplumber."""
    try:
        import pdfplumber
        st.write("Trying pdfplumber...")
        
        tables = []
        all_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for table_num, table in enumerate(page_tables):
                        if table and any(any(cell for cell in row) for row in table):
                            tables.append({
                                'page': page_num + 1,
                                'table_num': table_num + 1,
                                'data': table
                            })
                
                # Extract text
                text = page.extract_text()
                if text:
                    all_text.append(text)
        
        st.write(f"  pdfplumber found {len(tables)} tables")
        return tables, '\n'.join(all_text)
        
    except ImportError:
        st.write("pdfplumber not available")
        return [], ""
    except Exception as e:
        st.write(f"pdfplumber error: {e}")
        return [], ""

def extract_text_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    try:
        import pdfplumber
        with st.spinner("Extracting text..."):
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
    except ImportError:
        st.warning("⚠️ pdfplumber not available for text extraction")
        return ""
    except Exception as e:
        st.error(f"❌ Text extraction error: {str(e)}")
        return ""

def convert_to_markdown(text, tables):
    """Convert extracted content to markdown format"""
    markdown_parts = []
    
    # Add title
    markdown_parts.append("# Extracted PDF Content\n")
    
    # Add text content
    if text:
        markdown_parts.append("## Text Content\n")
        # Clean up text and format
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Simple formatting heuristics
                if line.isupper() and len(line) > 3:
                    formatted_lines.append(f"### {line}")
                elif line.endswith(':') and len(line) < 50:
                    formatted_lines.append(f"**{line}**")
                else:
                    formatted_lines.append(line)
        
        markdown_parts.append('\n'.join(formatted_lines))
        markdown_parts.append("\n---\n")
    
    # Add tables
    if tables:
        markdown_parts.append("## Tables\n")
        for i, table in enumerate(tables):
            markdown_parts.append(f"### Table {i+1}")
            if hasattr(table, 'df'):  # Camelot table
                df = table.df
            elif isinstance(table, pd.DataFrame):  # Tabula/pdfplumber table
                df = table
            else:
                continue
            
            # Create markdown table
            if not df.empty:
                # Get headers
                headers = df.columns.tolist()
                markdown_parts.append("| " + " | ".join(str(h) for h in headers) + " |")
                markdown_parts.append("| " + " | ".join(["---"] * len(headers)) + " |")
                
                # Add rows
                for _, row in df.iterrows():
                    row_values = [str(val) if pd.notna(val) else "" for val in row.values]
                    markdown_parts.append("| " + " | ".join(row_values) + " |")
                
                markdown_parts.append("")
    
    return '\n'.join(markdown_parts)

def get_download_link(data, filename, file_type):
    """Generate download link for files"""
    try:
        if file_type == "csv":
            if isinstance(data, pd.DataFrame):
                csv = data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">📥 Download CSV</a>'
            else:
                return "❌ Invalid data format for CSV"
        elif file_type == "json":
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            b64 = base64.b64encode(json_str.encode()).decode()
            href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">📥 Download JSON</a>'
        elif file_type == "txt":
            b64 = base64.b64encode(data.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">�� Download TXT</a>'
        elif file_type == "md":
            b64 = base64.b64encode(data.encode()).decode()
            href = f'<a href="data:file/md;base64,{b64}" download="{filename}.md">📥 Download Markdown</a>'
        else:
            return "❌ Unsupported file type"
        
        return href
    except Exception as e:
        return f"❌ Download error: {str(e)}"

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Advanced PDF Extractor</h1>', unsafe_allow_html=True)
    st.markdown("### Extract tables and text from scholarly papers and enterprise documents")
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to extract tables and text"
    )
    
    # Extraction options
    st.sidebar.markdown("### Extraction Methods")
    use_camelot = st.sidebar.checkbox("Use Camelot", value=True, help="Best for bordered tables")
    use_pdfplumber = st.sidebar.checkbox("Use pdfplumber", value=True, help="Fallback option")
    
    # Main content
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # File info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"📁 **File:** {uploaded_file.name} ({file_size:.1f} KB)")
            
            # Extraction process
            st.markdown("## 🔍 Extraction Results")
            
            extracted_tables = []
            extracted_text = ""
            method_used = ""
            
            # Try Camelot first
            if use_camelot:
                st.markdown("### 🐪 Camelot Extraction")
                camelot_tables = extract_with_camelot(tmp_file_path)
                if camelot_tables:
                    extracted_tables = camelot_tables
                    method_used = "camelot"
                    extracted_text = extract_text_with_pdfplumber(tmp_file_path)
            
            # Try pdfplumber
            if not extracted_tables and use_pdfplumber:
                st.markdown("### 📄 pdfplumber Extraction")
                pdfplumber_tables, pdfplumber_text = extract_with_pdfplumber(tmp_file_path)
                extracted_tables = pdfplumber_tables
                method_used = "pdfplumber"
                extracted_text = pdfplumber_text
            
            # Display results
            if extracted_tables or extracted_text:
                st.markdown("## 📊 Results")
                
                # Summary
                summary = {
                    "filename": uploaded_file.name,
                    "method": method_used,
                    "tables_found": len(extracted_tables) if extracted_tables else 0,
                    "text_length": len(extracted_text) if extracted_text else 0,
                    "word_count": len(extracted_text.split()) if extracted_text else 0,
                    "file_size_kb": file_size
                }
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Tables Found", summary["tables_found"])
                with col2:
                    st.metric("Words Extracted", summary["word_count"])
                with col3:
                    st.metric("Characters", summary["text_length"])
                with col4:
                    st.metric("Method Used", summary["method"].title())
                
                # Display tables
                if extracted_tables:
                    st.markdown("### 📋 Extracted Tables")
                    for i, table in enumerate(extracted_tables):
                        st.markdown(f"**Table {i+1}:**")
                        if hasattr(table, 'df'):  # Camelot table
                            st.dataframe(table.df)
                            st.markdown(get_download_link(table.df, f"table_{i+1}", "csv"), unsafe_allow_html=True)
                        elif isinstance(table, pd.DataFrame):  # Tabula/pdfplumber table
                            st.dataframe(table)
                            st.markdown(get_download_link(table, f"table_{i+1}", "csv"), unsafe_allow_html=True)
                        st.markdown("---")
                
                # Display text
                if extracted_text:
                    st.markdown("### 📝 Extracted Text")
                    
                    # Text preview
                    preview_length = 1000
                    if len(extracted_text) > preview_length:
                        st.text_area("Text Preview (first 1000 characters):", 
                                   extracted_text[:preview_length] + "...", 
                                   height=200)
                        st.markdown(f"*Full text has {len(extracted_text)} characters*")
                    else:
                        st.text_area("Extracted Text:", extracted_text, height=300)
                    
                    # Download text
                    st.markdown(get_download_link(extracted_text, "extracted_text", "txt"), unsafe_allow_html=True)
                
                # Generate and display markdown
                if extracted_text or extracted_tables:
                    st.markdown("### 📄 Markdown Export")
                    markdown_content = convert_to_markdown(extracted_text, extracted_tables)
                    st.text_area("Generated Markdown:", markdown_content, height=400)
                    st.markdown(get_download_link(markdown_content, "extracted_content", "md"), unsafe_allow_html=True)
                
                # Download summary
                st.markdown("### 📥 Download Summary")
                st.markdown(get_download_link(summary, "extraction_summary", "json"), unsafe_allow_html=True)
                
            else:
                st.error("❌ No content could be extracted from the PDF. Try a different file or check if the PDF contains extractable text.")
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    else:
        # Show instructions when no file is uploaded
        st.markdown("## 🚀 How to Use")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📋 Supported File Types
            - **PDF files** (text-based and scanned)
            - **Scholarly papers**
            - **Enterprise documents**
            - **Supply chain documents**
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Extraction Methods
            - **🐪 Camelot**: Best for bordered tables
            - **📄 pdfplumber**: Fallback option
            """)
        
        st.markdown("""
        ### 💡 Tips for Best Results
        1. **For tables**: Use PDFs with clear borders or grid lines
        2. **For text**: Works best with text-based PDFs (not scanned images)
        3. **For scholarly papers**: Most content will be extracted as text
        4. **For enterprise docs**: Tables and structured data will be detected automatically
        """)
        
        # Show sample output
        st.markdown("## 📊 Sample Output")
        sample_summary = {
            "filename": "example.pdf",
            "method": "camelot",
            "tables_found": 3,
            "text_length": 15420,
            "word_count": 2340,
            "file_size_kb": 245.6
        }
        st.json(sample_summary)

if __name__ == "__main__":
    main() 