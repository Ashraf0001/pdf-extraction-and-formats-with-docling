# PDF Table Extractor Suite

A comprehensive suite of tools for extracting tables and text from PDF documents, optimized for scholarly papers and enterprise supply chain documents.

## 🚀 Features

- **Multiple Extraction Methods**: Camelot, pdfplumber, and Tabula (with Java)
- **Batch Processing**: Process hundreds of PDFs efficiently
- **Parallel Processing**: Multi-threaded extraction for speed
- **Organized Output**: Structured results with summaries
- **No Java Required**: Works without Java installation (except for Tabula)
- **Multiple Interfaces**: Command-line, GUI, and Web interfaces

## 📁 Files Overview

### Core Extraction Scripts
- `alternative_pdf_extractor_no_java.py` - Single PDF extraction (no Java needed)
- `batch_pdf_processor.py` - Command-line batch processor
- `batch_processor_gui.py` - GUI batch processor
- `streamlit_alternative_extractor.py` - Web interface

### Original Scripts (for reference)
- `app.py` - Original Streamlit app
- `app_simple.py` - Simple version
- `app_enhanced.py` - Enhanced version
- `docling_pdf_table_extractor.py` - Docling-based extractor (requires models)

## 🛠️ Installation

1. **Activate your virtual environment:**
   ```bash
   .\venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install camelot-py[cv] pdfplumber pandas streamlit
   ```

3. **Optional - Install Java for Tabula:**
   - Download from: https://www.oracle.com/java/technologies/downloads/
   - Install the x64 Installer (.exe)
   - Restart your terminal

## 🎯 Usage

### 1. Single PDF Processing

**Command Line:**
```bash
python alternative_pdf_extractor_no_java.py your_file.pdf
```

**Web Interface:**
```bash
.\venv\Scripts\streamlit.exe run streamlit_alternative_extractor.py
```

### 2. Batch Processing

**Command Line:**
```bash
# Test mode (first 3 files)
python batch_pdf_processor.py input_folder output_folder --test

# Full batch processing
python batch_pdf_processor.py input_folder output_folder --workers 4
```

**GUI Interface:**
```bash
python batch_processor_gui.py
```

## 📊 Output Structure

### Single File Output
```
your_file_camelot_table_1.csv
your_file_camelot_table_2.csv
your_file_pdfplumber_text.txt
your_file_summary.json
```

### Batch Output
```
batch_output/
├── batch_summary.json          # Overall batch summary
├── batch_summary.csv           # CSV summary of all files
├── file1/
│   ├── camelot_table_1.csv
│   ├── camelot_table_2.csv
│   ├── extracted_text.txt
│   └── summary.json
├── file2/
│   ├── camelot_table_1.csv
│   ├── extracted_text.txt
│   └── summary.json
└── ...
```

## 🔧 Configuration Options

### Batch Processing Parameters
- `--workers`: Number of parallel workers (default: 4)
- `--test`: Test mode - process only first 3 files
- `input_dir`: Directory containing PDF files
- `output_dir`: Directory to save results

### GUI Options
- **Number of workers**: 1-8 parallel processes
- **Test mode**: Process only first 3 files
- **Input/Output directories**: Browse to select

## 📈 Performance

### Test Results
- **Single PDF**: ~10 seconds for 10 tables
- **Batch Processing**: ~2-3 seconds per PDF with 4 workers
- **Memory Usage**: ~100-200MB per worker
- **Output Size**: ~1-5MB per PDF (depending on content)

### Optimization Tips
1. **Use appropriate worker count**: 4 workers for most systems
2. **Test mode first**: Always test with `--test` flag
3. **Monitor memory**: Reduce workers if system becomes slow
4. **Organize input**: Group similar PDFs in folders

## 🎯 Use Cases

### Scholarly Papers
- Extract research tables and data
- Capture methodology sections
- Analyze citation patterns
- Extract abstracts and conclusions

### Enterprise Supply Chain Documents
- Extract inventory tables
- Capture pricing information
- Analyze supplier data
- Extract compliance information

## 🔍 Troubleshooting

### Common Issues

1. **"No tables found"**
   - Try different extraction methods
   - Check if PDF has actual tables
   - Verify PDF is not scanned image

2. **"Camelot not available"**
   - Install: `pip install camelot-py[cv]`
   - Check virtual environment activation

3. **"Java not found" (Tabula)**
   - Install Java from Oracle
   - Add Java to system PATH
   - Or use no-Java version

4. **"Memory errors"**
   - Reduce number of workers
   - Process smaller batches
   - Close other applications

### Performance Issues
- **Slow processing**: Reduce worker count
- **High memory usage**: Process fewer files simultaneously
- **Empty tables**: Try different extraction methods

## 📝 Logging

All batch operations create detailed logs:
- `batch_processing.log` - Detailed processing log
- Console output - Real-time progress
- Individual file summaries - Per-PDF results

## 🔄 Updates and Maintenance

### Regular Maintenance
1. **Update dependencies**: `pip install --upgrade camelot-py pdfplumber`
2. **Clear cache**: Remove old output directories
3. **Monitor logs**: Check for errors and performance issues

### Adding New Features
- Modify extraction functions in `batch_pdf_processor.py`
- Add new output formats in save functions
- Extend GUI options in `batch_processor_gui.py`

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Test with a simple PDF first
4. Verify all dependencies are installed

## 🎉 Success Metrics

Your current setup achieved:
- ✅ **10 tables extracted** from test PDF
- ✅ **34,764 characters** of text extracted
- ✅ **5,056 words** processed
- ✅ **10.37 seconds** processing time
- ✅ **100% success rate** for test file

Ready for batch processing of your scholarly papers and supply chain documents! 