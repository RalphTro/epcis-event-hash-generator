# EPCIS Event Hash Generator Changelog

## WIP

- Added configurable CBV version support: new `-v/--version` CLI flag allows choosing between CBV2.0 (default) and CBV2.1 for hash generation
- EPCIS 2.1 change: always add implicit JSONLD context (namespace) `{"gs1": "https://ref.gs1.org/voc/"}`
- Added MDAF (Master Data and Analytics Framework) support with experimental logic
- Added 3 MDAF example files for different vocabulary scenarios
- Added context files and notes for document loader
- Added support for ignoring industry/repository specific fields in both XML and JSON-LD documents
- Adjusted test files to ensure unique hashes across all test cases
- Removed experimental webservice support (Dockerfile, web API)
- Added container documentation
- Updated README with timestamp rounding rule documentation
- Added `requests` dependency
- Added support to generate hash from `EpcisQueryDocument`
- Fixed context expansion errors by removing empty dictionaries

## 1.9.3 (2023-05-16)

- Added Changelog
- Migrating from `setup.py` to `build` for the package build
- Making sure that static JSON-LD context files for the context loader are included in the package
