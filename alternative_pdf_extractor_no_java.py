#!/usr/bin/env python3
"""
Alternative PDF Table Extractor (No Java Required)
Uses Camelot and pdfplumber for table extraction without requiring Java/Tabula.
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path

def extract_with_camelot(pdf_path):
    """Extract tables using Camelot."""
    try:
        import camelot.io as camelot
        print("Trying Camelot...")
        
        # Try different table detection methods
        tables = []
        
        # Method 1: Lattice (for tables with borders)
        try:
            lattice_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            tables.extend(lattice_tables)
            print(f"  Lattice method found {len(lattice_tables)} tables")
        except Exception as e:
            print(f"  Lattice method failed: {e}")
        
        # Method 2: Stream (for tables without borders)
        try:
            stream_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            tables.extend(stream_tables)
            print(f"  Stream method found {len(stream_tables)} tables")
        except Exception as e:
            print(f"  Stream method failed: {e}")
        
        if tables:
            print(f"  Total Camelot tables: {len(tables)}")
            return tables
        else:
            print("  Camelot found no tables")
            return []
            
    except ImportError:
        print("Camelot not available")
        return []
    except Exception as e:
        print(f"Camelot error: {e}")
        return []

def extract_with_pdfplumber(pdf_path):
    """Extract tables and text using pdfplumber."""
    try:
        import pdfplumber
        print("Trying pdfplumber...")
        
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
        
        print(f"  pdfplumber found {len(tables)} tables")
        return tables, '\n'.join(all_text)
        
    except ImportError:
        print("pdfplumber not available")
        return [], ""
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return [], ""

def save_results(pdf_path, camelot_tables, pdfplumber_tables, pdfplumber_text):
    """Save extraction results to files."""
    base_name = Path(pdf_path).stem
    
    # Save Camelot tables
    if camelot_tables:
        for i, table in enumerate(camelot_tables):
            try:
                df = table.df
                if not df.empty:
                    filename = f"{base_name}_camelot_table_{i+1}.csv"
                    df.to_csv(filename, index=False)
                    print(f"Saved {filename}")
            except Exception as e:
                print(f"Error saving Camelot table {i+1}: {e}")
    
    # Save pdfplumber tables
    if pdfplumber_tables:
        for i, table_info in enumerate(pdfplumber_tables):
            try:
                df = pd.DataFrame(table_info['data'])
                if not df.empty:
                    filename = f"{base_name}_pdfplumber_table_{i+1}.csv"
                    df.to_csv(filename, index=False)
                    print(f"Saved {filename}")
            except Exception as e:
                print(f"Error saving pdfplumber table {i+1}: {e}")
    
    # Save pdfplumber text
    if pdfplumber_text:
        filename = f"{base_name}_pdfplumber_text.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pdfplumber_text)
        print(f"Saved {filename}")
    
    # Save summary
    summary = {
        "filename": Path(pdf_path).name,
        "camelot_tables": len(camelot_tables),
        "pdfplumber_tables": len(pdfplumber_tables),
        "text_length": len(pdfplumber_text),
        "word_count": len(pdfplumber_text.split()) if pdfplumber_text else 0
    }
    
    summary_filename = f"{base_name}_summary.json"
    with open(summary_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved {summary_filename}")

def main(pdf_path):
    """Main extraction function."""
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found")
        return
    
    print("=" * 50)
    print(f"Extracting from: {pdf_path}")
    print("=" * 50)
    
    # Extract with Camelot
    camelot_tables = extract_with_camelot(pdf_path)
    
    # Extract with pdfplumber
    pdfplumber_tables, pdfplumber_text = extract_with_pdfplumber(pdf_path)
    
    # Save results
    save_results(pdf_path, camelot_tables, pdfplumber_tables, pdfplumber_text)
    
    print("\nExtraction completed!")
    print(f"Total tables found: {len(camelot_tables) + len(pdfplumber_tables)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python alternative_pdf_extractor_no_java.py <pdf_file>")
        sys.exit(1)
    
    main(sys.argv[1]) 