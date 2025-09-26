# EPCIS Event Hashing Algorithm

## Core Concept

The algorithm creates syntax-agnostic hash IDs for EPCIS events by:

1. Extracting event data in canonical property order
2. Normalizing values according to strict rules
3. Concatenating into a pre-hash string
4. Applying standard hash algorithms (SHA-256, etc.)

## Canonical Property Order

Defined in `__init__.py` as `PROP_ORDER` - a nested tuple structure specifying:

- Sequence of properties to process (1-25)
- Child element ordering for complex fields
- Special handling for lists and nested structures

Key sequences:

1. `eventType` (though not explicitly in PROP_ORDER)
2. `eventTime`
3. `eventTimeZoneOffset`
4. `epcList` → `epc`
5. `parentID`
   6-12. Various input/output/quantity lists
6. `action`
7. `transformationID`
   15-16. `bizStep`, `disposition`
8. `persistentDisposition`
   18-19. `readPoint`, `bizLocation`
   20-22. Transaction/source/destination lists
9. `sensorElementList` (complex nested structure)
10. `ilmd` elements
11. User extension elements

## Key Normalization Rules

### Timestamps (`_fix_time_stamp_format` in `hash_generator.py`)

- Convert to UTC with 'Z' suffix
- Millisecond precision (pad with .000 if needed)
- Round 4th decimal place if present (5-9 rounds up)

### Numeric Values

- Remove trailing zeros
- No single quotes around numbers
- Preserve decimal precision as needed

### URI Normalization (`dl_normaliser.py`)

- Convert URN-based CBV values to GS1 Web URI format
- Expand CURIEs to full URIs
- Convert EPC URIs to canonical GS1 Digital Link
- Constrain GS1 Digital Link URIs (domain, query string, granularity)

### String Processing

- Trim leading/trailing whitespace
- UTF-8/ASCII lexical ordering for sorting
- Case-sensitive sorting

### Lists and Collections

- Sort child elements lexically
- Special type-first ordering for business transactions, sources, destinations
- Concatenate without separators (unless debugging with `join_by`)

## Implementation Files

- **`hash_generator.py`**: Core algorithm implementation

  - `derive_prehashes_from_events()` - Main pre-hash generation
  - `calculate_hashes_from_pre_hashes()` - Apply hash algorithms
  - `_fix_time_stamp_format()` - Timestamp normalization
  - `_pre_hash_from_epcis_event()` - Single event processing

- **`dl_normaliser.py`**: URI/Digital Link normalization
- **`__init__.py`**: Property order configuration (`PROP_ORDER`)

## Output Format

Final hash embedded in 'ni' URI scheme (RFC 6920):

```
ni:///{digest algorithm};{digest value}?ver={CBV version}
```

Example: `ni:///sha-256;B64HASH?ver=CBV2.0`

## Testing and Validation

Reference examples in `tests/examples/` with expected `.hashes` and `.prehashes` files for validation.
