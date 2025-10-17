# EPCIS Event Hash Generator - Project Index

## Project Overview

The EPCIS Event Hash Generator is a reference implementation for creating unique hash IDs for EPCIS events as specified in the GS1 Core Business Vocabulary (CBV) Standard 2.0. It provides syntax-agnostic hashing for EPCIS events in both XML and JSON-LD formats.

## Project Structure

### Core Package (`epcis_event_hash_generator/`)

- **Entry Point**: `__main__.py` - CLI interface and main execution logic
- **Core Logic**: `hash_generator.py` - Main hashing algorithm implementation
- **File Parsers**:
  - `events_from_file_reader.py` - Unified file reading interface
  - `xml_to_py.py` - XML EPCIS document parser
  - `json_to_py.py` - JSON-LD EPCIS document parser
- **Data Processing**:
  - `dl_normaliser.py` - Digital Link URI normalization
  - `json_xml_model_mismatch_correction.py` - Format compatibility fixes
- **Configuration**:
  - `__init__.py` - Package initialization with property order definitions
  - `context.py` - Import context management
  - `file_document_loader.py` - JSON-LD context document loading

### Testing (`tests/`)

- **Test Files**: Various test implementations (`test_*.py`)
- **Test Data**:
  - `examples/` - Sample EPCIS documents and expected outputs
  - `expected_equal/` - Reference documents for equivalence testing
- **Test Utilities**: `context.py`, `disable_test_annotation.py`

### Documentation (`docs/`)

- Algorithm illustrations and flow diagrams
- Visual examples of hash computation process

### Package Management

- `setup.py` - Package configuration and dependencies
- `requirements.txt` - Python dependencies
- `pypi_release.sh` - Release automation script

## Key Notes Files

- **[algorithm.md](algorithm.md)** - EPCIS event hashing algorithm details and canonical property order
- **[architecture.md](architecture.md)** - Code structure, key components, and data flow
- **[development.md](development.md)** - Development setup, testing strategies, and contribution guidelines
- **[usage.md](usage.md)** - CLI usage, API examples, and integration patterns

## Technical Stack

- **Language**: Python 3.6+
- **Key Dependencies**: PyLD (JSON-LD processing), python-dateutil, Flask
- **Supported Formats**: XML, JSON-LD EPCIS documents
- **Hash Algorithms**: SHA-256, SHA3-256, SHA-384, SHA-512

## Current Development Focus

Working on MDAF (Master Data and Analytics Framework) support as indicated by the current branch `MDAF-Support`.

## Quick Navigation

- **Algorithm Implementation**: See [algorithm.md](algorithm.md) and `hash_generator.py`
- **CLI Usage**: See [usage.md](usage.md) and `__main__.py`
- **Code Architecture**: See [architecture.md](architecture.md)
- **Testing**: See [development.md](development.md) and `tests/` directory
- **File Parsing**: See `events_from_file_reader.py`, `xml_to_py.py`, `json_to_py.py`
