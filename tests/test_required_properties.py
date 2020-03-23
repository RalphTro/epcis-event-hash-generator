try:
   from .context import epcis_event_hash_generator
except ImportError:
   from context import epcis_event_hash_generator


from epcis_event_hash_generator.epcis_event_hash_generator import epcis_hash
    

from os import walk

TEST_FILE_PATH = "examples/"
TEST_FILE_PATH_SAME_EVENT = "expected_equal/"


def test_distinct():
    """
    Assert that there are no collisions, i.e. different events must have different hashes.
    """
    all_hashes = []

    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if filename.endswith("xml"):
                all_hashes += epcis_hash(TEST_FILE_PATH + filename, "sha256")[0]
        break
    
    assert all_hashes
    assert len(all_hashes) == len(set(all_hashes))

    
def test_equal():    
    """
    Assert that different representations of the same events have the same hash.
    """
    for (_, _, filenames) in walk(TEST_FILE_PATH_SAME_EVENT):
        for filename in filenames:
            if filename.endswith("xml") or filename.endswith("json"):
                assert len(set(epcis_hash(TEST_FILE_PATH_SAME_EVENT + filename, "sha256")[0])) == 1
        break
