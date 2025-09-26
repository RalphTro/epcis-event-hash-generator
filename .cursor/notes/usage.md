# Usage Guide

## Command Line Interface

### Basic Usage

```bash
python3 -m epcis_event_hash_generator <file> [options]
```

### CLI Options (from `__main__.py`)

- **`-a, --algorithm`**: Hash algorithm (`sha256`, `sha3-256`, `sha384`, `sha512`)
- **`-l, --log`**: Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- **`-b, --batch`**: Write output to `.hashes` files instead of stdout
- **`-p, --prehash`**: Also output pre-hash strings (to `.prehashes` with `-b`)
- **`-j, --join`**: String to join pre-hash components (default: empty, useful for debugging with `\n`)
- **`-e, --enforce_format`**: Force format parsing (`XML`, `JSON`)

### Example Commands

```bash
# Basic hash generation
python3 -m epcis_event_hash_generator example.xml

# With pre-hash output and newline separation for debugging
python3 -m epcis_event_hash_generator example.xml -pj "\n"

# Batch processing with file output
python3 -m epcis_event_hash_generator *.xml -b

# Different hash algorithm
python3 -m epcis_event_hash_generator example.jsonld -a sha3-256

# Force JSON parsing regardless of file extension
python3 -m epcis_event_hash_generator data.txt -e JSON
```

## Programming API

### High-Level API

```python
from epcis_event_hash_generator.__main__ import epcis_hash_from_file

# Generate hashes from file
hashes, prehashes = epcis_hash_from_file(
    path="example.xml",
    hashalg="sha256",
    enforce="",
    join_by=""
)
```

### Low-Level API

```python
from epcis_event_hash_generator import hash_generator, events_from_file_reader

# Read events from file
events = events_from_file_reader.event_list_from_file("example.xml")

# Generate pre-hashes
prehashes = hash_generator.derive_prehashes_from_events(events)

# Calculate final hashes
hashes = hash_generator.calculate_hashes_from_pre_hashes(prehashes, "sha256")
```

## Supported Formats

### Input Files

- **XML EPCIS documents**: Auto-detected by `.xml` extension
- **JSON-LD EPCIS documents**: Auto-detected by `.json`, `.jsonld` extensions
- **Mixed formats**: Use `--enforce_format` to override detection

### Output

- **Default**: Hash values printed to stdout
- **Batch mode (`-b`)**:
  - `.hashes` files with newline-separated hash values
  - `.prehashes` files with pre-hash strings (if `-p` specified)

## Integration Patterns

### File Processing Pipeline

1. **Input Validation**: Check file existence and format
2. **Event Extraction**: Parse EPCIS document structure
3. **Hash Generation**: Apply canonical algorithm
4. **Output Management**: Handle single vs batch processing

### Error Handling

- **Malformed timestamps**: Logged as warnings, processed as-is
- **Missing files**: CLI exits with error code 1
- **Invalid formats**: Graceful fallback with logging

### Performance Considerations

- **Large files**: Process events individually to manage memory
- **Batch processing**: Use `-b` flag for multiple files
- **Debugging**: Use `-j "\n"` to inspect pre-hash string structure

## Testing and Validation

### Reference Examples

```bash
# Test with reference algorithm examples
python3 -m epcis_event_hash_generator tests/examples/ReferenceEventHashAlgorithm.xml

# Compare with expected output
python3 -m epcis_event_hash_generator tests/examples/ReferenceEventHashAlgorithm.xml -b
diff example.hashes tests/examples/ReferenceEventHashAlgorithm.hashes
```

### Equivalence Testing

Files in `tests/expected_equal/` contain different representations of the same events that should produce identical hashes.

## Common Use Cases

1. **Event ID Generation**: Populate `eventID` fields with intrinsic hash values
2. **Blockchain Storage**: Store hash values instead of full event data
3. **Duplicate Detection**: Compare hash values to identify duplicate events
4. **Data Integrity**: Verify event data hasn't been tampered with
5. **Event Matching**: Match error declarations to original events
