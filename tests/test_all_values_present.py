try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from os import walk

from epcis_event_hash_generator.hash_generator import epcis_hash, canonize_value
from epcis_event_hash_generator.json_to_py import event_list_from_epcis_document_json
from epcis_event_hash_generator.xml_to_py import event_list_from_epcis_document_xml

TEST_FILE_PATH = "examples/"


def _py_to_value_list(py_obj):
    """
    Transform a nested (Key, Value, Children) object tree into a list of (key, value) pairs.
    Ignoring times and eventID
    """
    key_values = []
    key, value, children = py_obj
    if "time" not in key.lower() and value != "" and key != "eventID":
        key_values.append((key, canonize_value(value)))
    for child in children:
        key_values += _py_to_value_list(child)
    return key_values


def _check_values(filename):
    if filename.endswith("xml"):
        print("Testing XML file " + filename)
        events = event_list_from_epcis_document_xml(filename)
    elif filename.endswith("json") or filename.endswith("jsonld"):
        print("Testing JSON file " + filename)
        events = event_list_from_epcis_document_json(filename)
    else:
        return False

    prehash_string_list = epcis_hash(filename, "sha256")[1]
    assert len(prehash_string_list) > 0

    for (py_obj, prehash_string) in zip(events[2], prehash_string_list):
        key_values = _py_to_value_list(py_obj)
        for key, value in key_values:
            msg = "Value '{}' for key '{}' not contained in prehash string\n{}\n for file {}".format(value,
                                                                                                     key,
                                                                                                     prehash_string,
                                                                                                     filename)
            assert prehash_string.find(value) >= 0, msg

    return True


def test_all_values_present():
    num_tested = 0
    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if _check_values(TEST_FILE_PATH + filename):
                num_tested += 1
    assert num_tested > 0, "No test files found"
