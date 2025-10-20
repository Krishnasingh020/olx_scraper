# OLX Car Cover Scraper

A Python web scraper that extracts car cover listings from OLX India and saves them in multiple formats (CSV, JSON, TXT).

## Features

- 🔍 **Automated Search**: Searches for "car cover" on OLX India
- 📊 **Multiple Output Formats**: Exports data to CSV, JSON, and text files
- 🛡️ **Robust Parsing**: Uses multiple extraction methods to handle website changes
- ⏱️ **Efficient**: Fast scraping with proper error handling
- 📁 **File Management**: Creates organized output files with complete listing details

## Files Generated

- `car_covers.csv` - Excel-compatible spreadsheet format
- `car_covers.json` - Structured data for programming use
- `car_covers.txt` - Human-readable text format
- `detailed_olx_page.html` - Raw HTML for debugging 

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Required Packages
Install the required dependencies:

```bash
pip install beautifulsoup4 lxml