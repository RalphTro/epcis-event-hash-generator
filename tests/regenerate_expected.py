# Regenerates the benchmark files: for every source document, compute the pre-hash and hash for
# BOTH CBV versions and write them under tests/examples/expected/<version>/.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from epcis_event_hash_generator.__main__ import epcis_hash_from_file

# source document/events live
DOCS = os.path.join(HERE, "examples", "documents")
EXPECTED = os.path.join(HERE, "examples", "expected")
VERSIONS = ["CBV2.0", "CBV2.1"]

print("Generating Event Hash-ID and Pre-Hash String")

for name in sorted(os.listdir(DOCS)):
    # Filter for only xml/json/jsonld
    if not name.endswith((".xml", ".json", ".jsonld")):
        continue
    base = os.path.splitext(name)[0]
    for v in VERSIONS:
        # compute hash and prehash string based on provided version
        hashes, prehashes = epcis_hash_from_file(os.path.join(DOCS, name), cbv_version=v)
        out = os.path.join(EXPECTED, v)
        # ensure expected/<version>/ folder exists
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, base + ".hashes"), "w") as f:
            # save the hash id(s)
            f.write("\n".join(hashes) + "\n")
        with open(os.path.join(out, base + ".prehashes"), "w") as f:
            f.write("\n".join(prehashes) + "\n")  # save the pre-hash string(s)
print("done")
