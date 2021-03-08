try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from os import walk

from epcis_event_hash_generator.__main__ import epcis_hash_from_file

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
                all_hashes += epcis_hash_from_file(TEST_FILE_PATH + filename, "sha256")[0]
        break

    assert all_hashes
    duplicates = set()
    for hash in all_hashes:
        if all_hashes.count(hash) > 1:
            duplicates.add(hash)

    assert len(duplicates) == 0, "The following hashes appeared multiple times: " + str(duplicates)


def test_equal():
    """
    Assert that different representations of the same events have the same hash.
    """
    for (_, _, filenames) in walk(TEST_FILE_PATH_SAME_EVENT):
        for filename in filenames:
            if filename.endswith("xml") or filename.endswith("json") or filename.endswith("jsonld"):
                assert len(set(epcis_hash_from_file(TEST_FILE_PATH_SAME_EVENT + filename, "sha256")[
                    0])) == 1, "The events in {} have different hashes!".format(
                    TEST_FILE_PATH_SAME_EVENT + filename)
        break
