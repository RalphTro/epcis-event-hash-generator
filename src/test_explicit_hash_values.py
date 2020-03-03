from .EpcisEventHashGenerator import xmlEpcisHash

from os import walk

TEST_FILE_PATH = "../testFiles/"

def testExplicitHashValues():  
    for (_, _, filenames) in walk(TEST_FILE_PATH):
        for filename in filenames:
            if filename.endswith("xml"):
                actualHashes = xmlEpcisHash(TEST_FILE_PATH + filename, "sha256")[0]
                with open(TEST_FILE_PATH + filename + '.hashes', 'r') as expectedfile:
                    expectedHashes = expectedfile.read().splitlines()
                print("Testing file " + filename)
                assert actualHashes == expectedHashes
        break
