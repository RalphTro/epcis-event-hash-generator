try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator

from epcis_event_hash_generator.__main__ import epcis_hash_from_file

DOCUMENTS_PATH = "examples/documents/"
# The "all possible fields" documents, provided in both XML and JSON.
EVENT_TYPES = ["ObjectEvent", "AggregationEvent", "TransactionEvent", "TransformationEvent", "AssociationEvent"]
VERSIONS = ["CBV2.0", "CBV2.1"]

def _assert_xml_json_match(event_type, cbv_version):
    # Same event in XML and JSON MUST produce the same pre-hash string AND the same hash id.
    xml_hashes, xml_prehashes = epcis_hash_from_file(
        DOCUMENTS_PATH + event_type + "_all_possible_fields.xml", cbv_version=cbv_version)
    json_hashes, json_prehashes = epcis_hash_from_file(
        DOCUMENTS_PATH + event_type + "_all_possible_fields.json", cbv_version=cbv_version)
    assert xml_prehashes == json_prehashes, \
        "{} {}: XML and JSON pre-hash strings differ".format(event_type, cbv_version)
    assert xml_hashes == json_hashes, \
        "{} {}: XML and JSON hash ids differ".format(event_type, cbv_version)

def test_all_possible_fields_xml_json_parity():
    # 5 event types x 2 versions = 10 XML/JSON parity checks.
    for event_type in EVENT_TYPES:
        for cbv_version in VERSIONS:
            _assert_xml_json_match(event_type, cbv_version)