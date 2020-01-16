from .EpcisEventHashGenerator import xmlEpcisHash

from os import walk

TEST_FILE_PATH = "../testFiles/"

def testDistinct():
    allHashes = []

    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if filename.endswith("xml"):
                allHashes += xmlEpcisHash(TEST_FILE_PATH + filename, "sha256")
        break
    # assert that there are no duplicates
    assert len(allHashes) == len(set(allHashes))
    
