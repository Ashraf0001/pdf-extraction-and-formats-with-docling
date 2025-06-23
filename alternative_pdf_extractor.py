import sys
import os
import json
import pandas as pd
from pathlib import Path

def extract_with_camelot(pdf_path):
    """Extract tables using Camelot (best for bordered tables)"""
    try:
        import camelot
        print("Trying Camelot...")
        tables = camelot.read_pdf(pdf_path, pages="all")
        if tables:
            print(f"Camelot found {len(tables)} tables")
            return tables
        else:
            print("Camelot found no tables")
            return []
    except ImportError:
        print("Camelot not installed. Install with: pip install camelot-py[cv]")
        return []
    except Exception as e:
        print(f"Camelot error: {e}")
        return []

def extract_with_tabula(pdf_path):
    """Extract tables using Tabula (robust for many layouts)"""
    try:
        import tabula
        print("Trying Tabula...")
        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
        if tables:
            print(f"Tabula found {len(tables)} tables")
            return tables
        else:
            print("Tabula found no tables")
            return []
    except ImportError:
        print("Tabula not installed. Install with: pip install tabula-py")
        return []
    except Exception as e:
        print(f"Tabula error: {e}")
        return []

def extract_with_pdfplumber(pdf_path):
    """Extract tables using pdfplumber (fallback option)"""
    try:
        import pdfplumber
        print("Trying pdfplumber...")
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table_num, table in enumerate(page_tables):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df['Page'] = page_num + 1
                        df['Table'] = table_num + 1
                        tables.append(df)
        if tables:
            print(f"pdfplumber found {len(tables)} tables")
            return tables
        else:
            print("pdfplumber found no tables")
            return []
    except ImportError:
        print("pdfplumber not installed. Install with: pip install pdfplumber")
        return []
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return []

def extract_text_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Text extraction error: {e}")
        return ""

def save_results(pdf_path, tables, text, method):
    """Save extracted tables and text to files"""
    base_name = os.path.splitext(pdf_path)[0]
    
    # Save tables
    if tables:
        for i, table in enumerate(tables):
            if hasattr(table, 'df'):  # Camelot table
                csv_file = f"{base_name}_{method}_table_{i+1}.csv"
                table.df.to_csv(csv_file, index=False)
                print(f"Saved {csv_file}")
            elif isinstance(table, pd.DataFrame):  # Tabula/pdfplumber table
                csv_file = f"{base_name}_{method}_table_{i+1}.csv"
                table.to_csv(csv_file, index=False)
                print(f"Saved {csv_file}")
    
    # Save text
    if text:
        text_file = f"{base_name}_{method}_text.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved {text_file}")
    
    # Save summary as JSON
    summary = {
        "filename": os.path.basename(pdf_path),
        "method": method,
        "tables_found": len(tables) if tables else 0,
        "text_length": len(text) if text else 0,
        "word_count": len(text.split()) if text else 0
    }
    
    json_file = f"{base_name}_{method}_summary.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved {json_file}")

def main(pdf_path):
    """Main extraction function"""
    print(f"Processing: {pdf_path}")
    print("=" * 50)
    
    # Try Camelot first (best for bordered tables)
    camelot_tables = extract_with_camelot(pdf_path)
    if camelot_tables:
        text = extract_text_with_pdfplumber(pdf_path)
        save_results(pdf_path, camelot_tables, text, "camelot")
        return
    
    # Try Tabula if Camelot failed
    tabula_tables = extract_with_tabula(pdf_path)
    if tabula_tables:
        text = extract_text_with_pdfplumber(pdf_path)
        save_results(pdf_path, tabula_tables, text, "tabula")
        return
    
    # Fallback to pdfplumber
    pdfplumber_tables = extract_with_pdfplumber(pdf_path)
    text = extract_text_with_pdfplumber(pdf_path)
    save_results(pdf_path, pdfplumber_tables, text, "pdfplumber")
    
    print("\nExtraction completed!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python alternative_pdf_extractor.py <path_to_pdf>")
        print("\nThis script tries multiple PDF extraction tools:")
        print("1. Camelot (best for bordered tables)")
        print("2. Tabula (robust for many layouts)")
        print("3. pdfplumber (fallback option)")
        print("\nInstall missing dependencies:")
        print("pip install camelot-py[cv] tabula-py pdfplumber")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found")
        sys.exit(1)
    
    main(pdf_path) 