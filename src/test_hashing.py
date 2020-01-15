from .EpcisEventHashGenerator import xmlEpcisHash

def testHashingWithSensorData():
    assert xmlEpcisHash("../testFiles/epcisDocWithSensorDataObjectEvent.xml", "sha256") == ["ni:///sha-256;cf346155eba383584e99334d0b1222e8895f607e0e2a9ed1be58cc36a7de5d64"]
    
def testHashingWithShippingAndTransporting():
    assert xmlEpcisHash("../testFiles/epcisDocWithShippingAndTransportingEvent.xml", "sha256") == ["ni:///sha-256;08fcd4e288a05137d14276784c5508dfca6cb560d22fec0b0133e7c56ca1b334", "ni:///sha-256;d10d4ceae8c7a44580695488d1c494aa27fda0ef6fa71d5c18f6cd8340a22d6a"]

def testHashingWithVariousEventTypes():
    assert xmlEpcisHash("../testFiles/epcisDocWithVariousEventTypes.xml", "sha256") == [
        'ni:///sha-256;70b37d30810f613523c00bd4d4ea3cffc06e721ab10a68d12925624b9f1d49c3',
        'ni:///sha-256;01971ceb9e54754015bbd115a0685de617ce4a65953e0c6dfba02469b6ef6193',
        'ni:///sha-256;d5dee3111979646fb492f3fd0242a11d848df91facebf1e47718f94cb8b23985',
        'ni:///sha-256;31e0e164361556f0e6172ac9d30e7df29da01e3fec433563e200718f29fd456d',
        'ni:///sha-256;8eef3b5f7036ef9f39bb7ba9f37dcd2b69b127173c7b01a23f4587e81fa11b65',
        'ni:///sha-256;16585edb3afadf2d3741c614b430917363eb7dfa6016bb1237cbaeaf2b5c1333',
        'ni:///sha-256;6063b85954571532862c216921fe48700da96d42f6174eb68f4e293572ddc985',
        'ni:///sha-256;f0263a38fe5c2f8583c95b31a48303498fa6cb6a3b4e823403e3977574bfce88',
        'ni:///sha-256;bf05637279e89d39fa3b846155619b93669d0cfd590ea1e556ad05d174bd7664',
        'ni:///sha-256;ebc119e75f8787dfc99798f18f93fd968f0b6ee6796d7e708037e4836e06ae9f'
    ]

def testHashingWithTagAndError():
    assert xmlEpcisHash("../testFiles/epcisDocWithXMLstartTagAndErrorDeclaration.xml", "sha256") == []

    
