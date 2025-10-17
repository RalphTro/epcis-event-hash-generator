# Code Architecture

## Data Flow

1. **File Input** → `events_from_file_reader.py`
2. **Format Detection** → Dispatch to XML or JSON parser
3. **Parsing** → `xml_to_py.py` or `json_to_py.py`
4. **Event Extraction** → Normalized Python objects
5. **Hash Generation** → `hash_generator.py`
6. **Output** → Hashes and optional pre-hashes

## Core Components

### Entry Points

- **`__main__.py`**: CLI interface with argparse
  - `main()` - Primary entry point
  - `command_line_parsing()` - Argument handling
  - `epcis_hash_from_file()` - High-level API

### File Parsing Layer

- **`events_from_file_reader.py`**: Unified file reading interface

  - `event_list_from_file()` - Main function, auto-detects format
  - `_event_list_from_epcis_document_xml/json()` - Format-specific readers

- **`xml_to_py.py`**: XML EPCIS parsing

  - Handles XML namespace resolution
  - Converts XML structure to Python objects

- **`json_to_py.py`**: JSON-LD EPCIS parsing
  - Uses PyLD for JSON-LD expansion
  - Handles context resolution via `file_document_loader.py`

### Processing Layer

- **`hash_generator.py`**: Core hashing logic

  - Property order traversal
  - Value normalization
  - Pre-hash string generation
  - Hash calculation

- **`dl_normaliser.py`**: URI normalization
  - GS1 Digital Link processing
  - CURIE expansion
  - CBV vocabulary mapping

### Support Modules

- **`context.py`**: Import path resolution for module vs script execution
- **`file_document_loader.py`**: Custom JSON-LD document loader for offline context files
- **`json_xml_model_mismatch_correction.py`**: Format compatibility fixes

## Key Design Patterns

### Modular Parsing

- Format-agnostic interface in `events_from_file_reader`
- Separate parsers for XML and JSON-LD maintain format-specific logic
- Common output format (Python objects) for downstream processing

### Configuration-Driven Processing

- `PROP_ORDER` in `__init__.py` defines canonical ordering
- Declarative structure allows easy maintenance of algorithm specification

### Error Handling

- Graceful handling of malformed timestamps
- Logging throughout for debugging
- File I/O error management

### Testing Strategy

- Extensive test data in `tests/examples/`
- Expected output files (`.hashes`, `.prehashes`) for validation
- Format equivalence testing in `tests/expected_equal/`

## Dependencies

### External Libraries

- **PyLD**: JSON-LD processing and expansion
- **python-dateutil**: Robust timestamp parsing
- **Flask**: Web interface capabilities (if needed)

### Internal Dependencies

- Tight coupling between `hash_generator.py` and property order configuration
- `dl_normaliser` used by hash generator for URI processing
- Context files in `gs1_web_voc_context_files/` for JSON-LD processing

## Extension Points

- **Custom hash algorithms**: Configurable in CLI and hash generator
- **Property order modifications**: Update `PROP_ORDER` in `__init__.py`
- **Additional normalizers**: Extend `dl_normaliser.py` or add new modules
- **Format support**: Add new parsers following existing patterns
