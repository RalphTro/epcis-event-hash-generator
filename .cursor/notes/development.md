# Development Guide

## Development Setup

### Requirements

- Python 3.6+ (specified in `setup.py`)
- Dependencies from `requirements.txt`:
  - `python-dateutil>=2.8`
  - `Flask>=1.1`
  - `PyLD==2.0.3`
  - `requests>=2.25`

### Installation

```bash
# Development installation
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Testing Strategy

### Test Structure (`tests/` directory)

- **Unit Tests**: `test_*.py` files for specific functionality
- **Integration Tests**: Full workflow testing with sample data
- **Reference Data**: `examples/` and `expected_equal/` directories

### Key Test Files

- **`test_explicit_hash_values.py`**: Validates against known hash values
- **`test_xml_to_py.py`**: XML parsing functionality
- **`test_bare_string_normalisation.py`**: String processing rules
- **`test_required_properties.py`**: Required property validation
- **`test_all_values_present.py`**: Comprehensive data coverage

### Test Data Organization

- **`examples/`**: Sample EPCIS documents with expected `.hashes` and `.prehashes` outputs
- **`expected_equal/`**: Different representations of same events (should yield identical hashes)

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_explicit_hash_values.py

# Run with verbose output
python -m pytest tests/ -v
```

## Code Style and Conventions

### Documentation Standards

- **Module docstrings**: Follow format in existing files
- **Function docstrings**: Describe parameters and return values
- **Copyright headers**: Include in all new files

### Import Patterns

```python
# Conditional imports for module vs script execution
try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401
```

### Error Handling

- Use `logging` module for debug/warning messages
- Graceful handling of malformed data with appropriate warnings
- Preserve original data when normalization fails

## Current Development Focus

### MDAF Support (Current Branch)

Working on Master Data and Analytics Framework integration as indicated by branch `MDAF-Support`.

### Key Development Areas

1. **Algorithm Compliance**: Ensure strict adherence to CBV 2.0 specification
2. **Format Support**: Maintain parity between XML and JSON-LD processing
3. **Performance**: Optimize for large EPCIS documents
4. **Testing**: Comprehensive coverage of edge cases

## Contribution Guidelines

### Code Changes

1. **Algorithm modifications**: Update `PROP_ORDER` in `__init__.py` if needed
2. **New normalizers**: Add to or extend `dl_normaliser.py`
3. **Parser enhancements**: Modify format-specific parsers (`xml_to_py.py`, `json_to_py.py`)

### Testing Requirements

- Add test cases for new functionality
- Update reference data if algorithm changes
- Validate against existing test suite

### Documentation Updates

- Update `README.md` for user-facing changes
- Add to `Changelog.md` following conventions in `.cursor/rules/changelog-conventions.mdc`
- Update algorithm documentation for specification changes

## Release Process

### Package Management

- **`setup.py`**: Package configuration and metadata
- **`pypi_release.sh`**: Automated release script
- **Version numbering**: Semantic versioning in `setup.py`

### Release Checklist

1. Update version in `setup.py`
2. Update `Changelog.md` with release notes
3. Run full test suite
4. Create release via `pypi_release.sh`
5. Tag release in Git

## Debugging and Troubleshooting

### Common Issues

- **Timestamp parsing**: Check `_fix_time_stamp_format()` in `hash_generator.py`
- **URI normalization**: Debug `dl_normaliser.py` functions
- **Property ordering**: Verify `PROP_ORDER` configuration
- **Context loading**: Check JSON-LD context files in `gs1_web_voc_context_files/`

### Debug Tools

- Use `-j "\n"` CLI flag to inspect pre-hash string structure
- Enable debug logging with `-l DEBUG`
- Compare `.prehashes` output with expected values

### Performance Profiling

- Monitor memory usage with large EPCIS documents
- Profile JSON-LD expansion performance
- Optimize property traversal for complex events
