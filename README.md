# win-flash-finder

An ultra-fast, multithreaded file search CLI for Windows (and cross-platform) with instant specialized finders for PDFs, Python `.pth` path configuration files, office documents, and custom regex searches. Built using standard Python 3 standard library only.

## Features

- **Multithreaded Directory Scanning**: High throughput using `concurrent.futures` and `os.scandir`.
- **Specialized Instant Presets**: Pre-configured filters for quick execution:
  - `pdf`: Instant PDF search
  - `pth`: Find Python `.pth` path setup files across python environments
  - `docs`: Standard document formats (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`, `.rtf`, `.odt`)
  - `code`: Common code source files (`.py`, `.js`, `.ts`, `.rs`, `.go`, etc.)
  - `archive`: Compressed archives (`.zip`, `.7z`, `.tar`, `.rar`, etc.)
- **Pattern Matching**: RegEx filtering on filenames.
- **Zero External Dependencies**: Pure Python standard library implementation.

## Usage

```bash
# Find all PDF files in current directory
python -m win_flash_finder.cli -p pdf

# Find python .pth files in Python installation directory
python -m win_flash_finder.cli C:\Python311 -p pth

# Search for files matching regex pattern
python -m win_flash_finder.cli C:\Users -n "report.*2023" -e pdf

# Limit search depth to 2 levels
python -m win_flash_finder.cli . -d 2
```

## Running Tests

```bash
python -m unittest discover tests
```

---
_This project was scaffolded with the help of an AI agent._
