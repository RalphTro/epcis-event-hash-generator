from .epcis_event_hash_generator import epcis_hash

from os import walk, path

TEST_FILE_PATH = "../testFiles/examples/"

def test_explicit_hash_values():  
    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if filename.endswith("xml") or filename.endswith("json"):
                print("Testing file " + filename)
                actualHashes = epcis_hash(TEST_FILE_PATH + filename, "sha256")[0]
                assert len(actualHashes) > 0
                with open(TEST_FILE_PATH + path.splitext(filename)[0] + '.hashes', 'r') as expectedfile:
                    expectedHashes = expectedfile.read().splitlines()
                assert actualHashes == expectedHashes
        break


