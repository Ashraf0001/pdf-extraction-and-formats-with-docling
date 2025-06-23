#!/usr/bin/env python3
"""
Batch PDF Processor GUI
Simple GUI interface for batch processing PDFs.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import queue
import time

# Import the batch processing functions
from batch_pdf_processor import process_single_pdf, process_pdfs_batch

class BatchProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch PDF Table Extractor")
        self.root.geometry("800x600")
        
        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.workers = tk.IntVar(value=4)
        self.test_mode = tk.BooleanVar(value=False)
        
        # Message queue for logging
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.update_log()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Input directory
        ttk.Label(main_frame, text="Input Directory (PDFs):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Workers
        ttk.Label(options_frame, text="Number of workers:").grid(row=0, column=0, sticky="w")
        workers_spinbox = ttk.Spinbox(options_frame, from_=1, to=8, textvariable=self.workers, width=10)
        workers_spinbox.grid(row=0, column=1, sticky="w", padx=5)
        
        # Test mode
        ttk.Checkbutton(options_frame, text="Test mode (process only first 3 files)", 
                       variable=self.test_mode).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Start Processing", command=self.start_processing)
        self.process_button.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Log area
        ttk.Label(main_frame, text="Processing Log:").grid(row=5, column=0, sticky="w", pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5)
    
    def browse_input(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def log_message(self, message):
        """Add message to log queue"""
        self.log_queue.put(message)
    
    def update_log(self):
        """Update log display from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_log)
    
    def start_processing(self):
        """Start batch processing in a separate thread"""
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if not os.path.exists(self.input_dir.get()):
            messagebox.showerror("Error", "Input directory does not exist")
            return
        
        # Disable UI during processing
        self.process_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Processing...")
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """Process files in background thread"""
        try:
            input_dir = self.input_dir.get()
            output_dir = self.output_dir.get()
            workers = self.workers.get()
            test_mode = self.test_mode.get()
            
            self.log_message(f"Starting batch processing...")
            self.log_message(f"Input directory: {input_dir}")
            self.log_message(f"Output directory: {output_dir}")
            self.log_message(f"Workers: {workers}")
            
            if test_mode:
                self.log_message("Running in TEST MODE - will process only first 3 files")
                # Process only first 3 files for testing
                pdf_files = list(Path(input_dir).glob("*.pdf"))[:3]
                if pdf_files:
                    for pdf_file in pdf_files:
                        self.log_message(f"Processing: {pdf_file.name}")
                        result = process_single_pdf(pdf_file, Path(output_dir))
                        if result.get("status") == "success":
                            self.log_message(f"✓ Completed {pdf_file.name} - {result.get('total_tables', 0)} tables found")
                        else:
                            self.log_message(f"✗ Failed {pdf_file.name}: {result.get('error', 'Unknown error')}")
                else:
                    self.log_message("No PDF files found for testing")
            else:
                # Full batch processing
                process_pdfs_batch(input_dir, output_dir, workers)
            
            self.log_message("Batch processing completed!")
            
        except Exception as e:
            self.log_message(f"Error during processing: {e}")
        finally:
            # Re-enable UI
            self.root.after(0, self.processing_finished)
    
    def processing_finished(self):
        """Called when processing is finished"""
        self.process_button.config(state='normal')
        self.progress.stop()
        self.status_var.set("Ready")
        messagebox.showinfo("Complete", "Batch processing completed! Check the output directory for results.")

def main():
    root = tk.Tk()
    app = BatchProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 