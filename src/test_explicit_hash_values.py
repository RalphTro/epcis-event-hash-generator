from .EpcisEventHashGenerator import xmlEpcisHash

def testHashingWithSensorData():
    assert xmlEpcisHash("../testFiles/epcisDocWithSensorDataObjectEvent.xml", "sha256") == ["ni:///sha-256;69067195a37004e9255c8716940cc94b14b0c87a893830ac01349a52b3f8ed1a"]
    
def testHashingWithShippingAndTransporting():
    assert xmlEpcisHash("../testFiles/epcisDocWithShippingAndTransportingEvent.xml", "sha256") == ["ni:///sha-256;d56219c5c5643f4eca2e0581c0e3653677470db122c51d9e14df19f47e4b2062", "ni:///sha-256;d10d4ceae8c7a44580695488d1c494aa27fda0ef6fa71d5c18f6cd8340a22d6a"]

def testHashingWithVariousEventTypes():
    assert xmlEpcisHash("../testFiles/epcisDocWithVariousEventTypes.xml", "sha256") == [
        'ni:///sha-256;8bbeabedf8b7021916aeafbdd1bf13ddd19dcc3fc068cbecefbc31767dce2449',
        'ni:///sha-256;ad24ae1e1f3049fbf2944adb0a0dfa1b917804803c0df78e641ec67055da4353',
        'ni:///sha-256;d5dee3111979646fb492f3fd0242a11d848df91facebf1e47718f94cb8b23985',
        'ni:///sha-256;0bc08867864c1cd52af29ee5a62bf850f0d5f447bf5206f4a2375628cb6fde9a',
        'ni:///sha-256;31e0e164361556f0e6172ac9d30e7df29da01e3fec433563e200718f29fd456d',
        'ni:///sha-256;8eef3b5f7036ef9f39bb7ba9f37dcd2b69b127173c7b01a23f4587e81fa11b65',
        'ni:///sha-256;c5d71e7902c2ab1b02c6b3bb0c49751c29f033cdda66793415b4ef934a2237ad',
        'ni:///sha-256;c4df36fad71000c25fd49e8164b31021a77a4da679ce7868d3fa8d1e32a1828a',
        'ni:///sha-256;6a46a3082263a132770643250e8319f3094c5507be6702704dbd7f9153dfc576',
        'ni:///sha-256;65a0d8df9d2a7402cb058a1e9e2c0673f39235bc87cb6bca44676e0ec6b70215',
        'ni:///sha-256;b340af2de4653420ebc4d9d63b5d76293d629689ec0f3dc97b181aabcf11f677',
        'ni:///sha-256;c4ecf9497d3af079aafbf0dde2ddb56df0438b9582615ea3fcf02b6053fab1f7',
        'ni:///sha-256;ebc119e75f8787dfc99798f18f93fd968f0b6ee6796d7e708037e4836e06ae9f'
    ]

def testHashingWithTagAndError():
    assert xmlEpcisHash("../testFiles/epcisDocWithXMLstartTagAndErrorDeclaration.xml", "sha256") == ['ni:///sha-256;9cec2d73b101aaab278688be8b2cbfa114860b10c80a3b94f61fdbd19e5ab03c']

    
