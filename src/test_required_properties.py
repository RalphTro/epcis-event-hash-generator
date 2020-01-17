from .EpcisEventHashGenerator import xmlEpcisHash

from os import walk

TEST_FILE_PATH = "../testFiles/"
TEST_FILE_PATH_SAME_EVENT = "../testFiles/reordering/"

def testDistinct():
    """
    Assert that there are no collisions, i.e. different events must have different hashes.
    """
    allHashes = []

    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if filename.endswith("xml"):
                allHashes += xmlEpcisHash(TEST_FILE_PATH + filename, "sha256")
        break
    
    assert len(allHashes) == len(set(allHashes))
    
def testEqual():    
    """
    Assert that different representations of the same events have the same hash.
    """
    for (_, _, filenames) in walk(TEST_FILE_PATH_SAME_EVENT):
        for filename in filenames:
            if filename.endswith("xml"):
                assert len(set(xmlEpcisHash(TEST_FILE_PATH_SAME_EVENT + filename, "sha256"))) == 1
        break
