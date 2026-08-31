try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from os import walk, path

from epcis_event_hash_generator.__main__ import epcis_hash_from_file

DOCUMENTS_PATH = "examples/documents/"   # source EPCIS documents (xml / json / jsonld)
EXPECTED_PATH = "examples/expected/"     # benchmark outputs, split per version: CBV2.0/ and CBV2.1/

def _check_version(cbv_version):
    # For every source document, compute its hash + pre-hash for provided CBV version and compare with benchmark
    num_tested = 0

    for (_, _, filenames) in walk(DOCUMENTS_PATH):
        for filename in filenames:
            if not (filename.endswith("xml") or filename.endswith("json") or filename.endswith("jsonld")):
                continue
            base = path.splitext(filename)[0]
            hashes, prehashes = epcis_hash_from_file(DOCUMENTS_PATH + filename, cbv_version=cbv_version)
            assert len(hashes) > 0
            with open(EXPECTED_PATH + cbv_version + "/" + base + ".hashes") as expected_file:
                expected_hashes = expected_file.read().splitlines()  # one hash per event
            with open(EXPECTED_PATH + cbv_version + "/" + base + ".prehashes") as expected_file:
                expected_prehashes = expected_file.read().splitlines()  # one pre-hash string per event
            assert prehashes == expected_prehashes, "{} pre-hash for {} is not as expected!".format(cbv_version,
                                                                                                    filename)
            num_tested += 1
        break
    assert num_tested > 20



# Test all Hash-ID and Pre-Hash against EPCIS/CBV 2.0 rules
def test_cbv20_hashes():
    _check_version("CBV2.0")

# Test all Hash-ID and Pre-Hash against EPCIS/CBV 2.1 rules
def test_cbv21_hashes():
    _check_version("CBV2.1")