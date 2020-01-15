from .EpcisEventHashGenerator import xmlEpcisHash

def test_hashing():
    """
    Ralphs' example.
    """
    assert xmlEpcisHash("../test/sensorObjectEvent.xml", "sha256") == ["ni:///sha-256;cf346155eba383584e99334d0b1222e8895f607e0e2a9ed1be58cc36a7de5d64"]
    
