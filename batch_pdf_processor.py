#!/usr/bin/env python3
"""
Batch PDF Table Extractor
Process multiple PDFs efficiently with progress tracking and organized output.
"""

import os
import sys
import json
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)

def extract_with_camelot(pdf_path):
    """Extract tables using Camelot."""
    try:
        import camelot.io as camelot
        logging.info(f"Trying Camelot on {Path(pdf_path).name}...")
        
        tables = []
        
        # Method 1: Lattice (for tables with borders)
        try:
            lattice_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            tables.extend(lattice_tables)
            logging.info(f"  Lattice method found {len(lattice_tables)} tables")
        except Exception as e:
            logging.warning(f"  Lattice method failed: {e}")
        
        # Method 2: Stream (for tables without borders)
        try:
            stream_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            tables.extend(stream_tables)
            logging.info(f"  Stream method found {len(stream_tables)} tables")
        except Exception as e:
            logging.warning(f"  Stream method failed: {e}")
        
        if tables:
            logging.info(f"  Total Camelot tables: {len(tables)}")
            return tables
        else:
            logging.info("  Camelot found no tables")
            return []
            
    except ImportError:
        logging.error("Camelot not available")
        return []
    except Exception as e:
        logging.error(f"Camelot error: {e}")
        return []

def extract_with_pdfplumber(pdf_path):
    """Extract tables and text using pdfplumber."""
    try:
        import pdfplumber
        logging.info(f"Trying pdfplumber on {Path(pdf_path).name}...")
        
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
        
        logging.info(f"  pdfplumber found {len(tables)} tables")
        return tables, '\n'.join(all_text)
        
    except ImportError:
        logging.error("pdfplumber not available")
        return [], ""
    except Exception as e:
        logging.error(f"pdfplumber error: {e}")
        return [], ""

def process_single_pdf(pdf_path, output_dir):
    """Process a single PDF and save results."""
    pdf_name = Path(pdf_path).stem
    pdf_dir = output_dir / pdf_name
    
    # Create directory for this PDF
    pdf_dir.mkdir(exist_ok=True)
    
    try:
        logging.info(f"Processing: {Path(pdf_path).name}")
        start_time = time.time()
        
        # Extract with Camelot
        camelot_tables = extract_with_camelot(pdf_path)
        
        # Extract with pdfplumber
        pdfplumber_tables, pdfplumber_text = extract_with_pdfplumber(pdf_path)
        
        # Save Camelot tables
        camelot_saved = 0
        for i, table in enumerate(camelot_tables):
            try:
                df = table.df
                if not df.empty:
                    filename = pdf_dir / f"camelot_table_{i+1}.csv"
                    df.to_csv(filename, index=False)
                    camelot_saved += 1
            except Exception as e:
                logging.error(f"Error saving Camelot table {i+1}: {e}")
        
        # Save pdfplumber tables
        pdfplumber_saved = 0
        for i, table_info in enumerate(pdfplumber_tables):
            try:
                df = pd.DataFrame(table_info['data'])
                if not df.empty:
                    filename = pdf_dir / f"pdfplumber_table_{i+1}.csv"
                    df.to_csv(filename, index=False)
                    pdfplumber_saved += 1
            except Exception as e:
                logging.error(f"Error saving pdfplumber table {i+1}: {e}")
        
        # Save text
        text_filename = pdf_dir / "extracted_text.txt"
        if pdfplumber_text:
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(pdfplumber_text)
        
        # Create summary
        processing_time = time.time() - start_time
        summary = {
            "filename": Path(pdf_path).name,
            "processing_time_seconds": round(processing_time, 2),
            "camelot_tables_found": len(camelot_tables),
            "camelot_tables_saved": camelot_saved,
            "pdfplumber_tables_found": len(pdfplumber_tables),
            "pdfplumber_tables_saved": pdfplumber_saved,
            "text_length": len(pdfplumber_text),
            "word_count": len(pdfplumber_text.split()) if pdfplumber_text else 0,
            "total_tables": len(camelot_tables) + len(pdfplumber_tables),
            "status": "success"
        }
        
        # Save summary
        summary_filename = pdf_dir / "summary.json"
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"Completed {Path(pdf_path).name} in {processing_time:.2f}s - {summary['total_tables']} tables found")
        return summary
        
    except Exception as e:
        logging.error(f"Error processing {Path(pdf_path).name}: {e}")
        error_summary = {
            "filename": Path(pdf_path).name,
            "status": "error",
            "error": str(e)
        }
        error_filename = pdf_dir / "error.json"
        with open(error_filename, 'w') as f:
            json.dump(error_summary, f, indent=2)
        return error_summary

def process_pdfs_batch(input_dir, output_dir, max_workers=4):
    """Process multiple PDFs with parallel processing."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(exist_ok=True)
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        logging.error(f"No PDF files found in {input_dir}")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Create batch summary
    batch_summary = {
        "batch_start_time": datetime.now().isoformat(),
        "input_directory": str(input_path),
        "output_directory": str(output_path),
        "total_files": len(pdf_files),
        "processed_files": 0,
        "successful_files": 0,
        "failed_files": 0,
        "total_tables_found": 0,
        "total_processing_time": 0,
        "file_results": []
    }
    
    start_time = time.time()
    
    # Process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_pdf = {
            executor.submit(process_single_pdf, pdf_file, output_path): pdf_file 
            for pdf_file in pdf_files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_pdf):
            pdf_file = future_to_pdf[future]
            try:
                result = future.result()
                batch_summary["file_results"].append(result)
                batch_summary["processed_files"] += 1
                
                if result.get("status") == "success":
                    batch_summary["successful_files"] += 1
                    batch_summary["total_tables_found"] += result.get("total_tables", 0)
                else:
                    batch_summary["failed_files"] += 1
                    
            except Exception as e:
                logging.error(f"Error processing {pdf_file.name}: {e}")
                batch_summary["failed_files"] += 1
                batch_summary["file_results"].append({
                    "filename": pdf_file.name,
                    "status": "error",
                    "error": str(e)
                })
    
    # Finalize batch summary
    batch_summary["total_processing_time"] = time.time() - start_time
    batch_summary["batch_end_time"] = datetime.now().isoformat()
    
    # Save batch summary
    batch_summary_file = output_path / "batch_summary.json"
    with open(batch_summary_file, 'w') as f:
        json.dump(batch_summary, f, indent=2)
    
    # Create CSV summary
    successful_results = [r for r in batch_summary["file_results"] if r.get("status") == "success"]
    if successful_results:
        df = pd.DataFrame(successful_results)
        csv_summary_file = output_path / "batch_summary.csv"
        df.to_csv(csv_summary_file, index=False)
    
    # Print final summary
    logging.info("=" * 60)
    logging.info("BATCH PROCESSING COMPLETED")
    logging.info("=" * 60)
    logging.info(f"Total files: {batch_summary['total_files']}")
    logging.info(f"Successful: {batch_summary['successful_files']}")
    logging.info(f"Failed: {batch_summary['failed_files']}")
    logging.info(f"Total tables found: {batch_summary['total_tables_found']}")
    logging.info(f"Total processing time: {batch_summary['total_processing_time']:.2f} seconds")
    logging.info(f"Results saved to: {output_path}")
    logging.info("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Batch PDF Table Extractor")
    parser.add_argument("input_dir", help="Directory containing PDF files")
    parser.add_argument("output_dir", help="Directory to save results")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers (default: 4)")
    parser.add_argument("--test", action="store_true", help="Test mode - process only first 3 files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        logging.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    logging.info(f"Starting batch processing...")
    logging.info(f"Input directory: {args.input_dir}")
    logging.info(f"Output directory: {args.output_dir}")
    logging.info(f"Workers: {args.workers}")
    
    if args.test:
        logging.info("Running in TEST MODE - will process only first 3 files")
        # Limit to first 3 files for testing
        pdf_files = list(Path(args.input_dir).glob("*.pdf"))[:3]
        if pdf_files:
            for pdf_file in pdf_files:
                process_single_pdf(pdf_file, Path(args.output_dir))
        else:
            logging.error("No PDF files found for testing")
    else:
        process_pdfs_batch(args.input_dir, args.output_dir, args.workers)

if __name__ == "__main__":
    main() 