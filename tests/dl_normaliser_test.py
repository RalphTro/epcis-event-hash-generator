try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.dl_normaliser import normaliser


def test_good_epc_conversion():
    """ Testing few EPC URIs (all schemes) """
    assert normaliser('urn:epc:id:sgtin:4012345.011111.98%22') == "https://id.gs1.org/01/04012345111118/21/98%22"
    assert normaliser('urn:epc:id:sgtin:415056789012.0.987654') == "https://id.gs1.org/01/04150567890128/21/987654"
    assert normaliser(
        'urn:epc:id:sgtin:0614141.812345.6789%2F%26%25%22!%3F()') == "https://id.gs1.org/01/80614141123458/21/6789%2F%26%25%22%21%3F%28%29"
    assert normaliser('urn:epc:id:sscc:4012345.3111111111') == "https://id.gs1.org/00/340123451111111111"
    assert normaliser('urn:epc:id:sgln:4012345.00005.122') == "https://id.gs1.org/414/4012345000054/254/122"
    assert normaliser('urn:epc:id:sgln:4012345.00005.0') == "https://id.gs1.org/414/4012345000054"
    assert normaliser('urn:epc:id:grai:4012345.00022.334455') == "https://id.gs1.org/8003/04012345000221334455"
    assert normaliser('urn:epc:id:giai:4012345.ABC345') == "https://id.gs1.org/8004/4012345ABC345"
    assert normaliser('urn:epc:id:gsrn:4012345.0000006765') == "https://id.gs1.org/8018/401234500000067657"
    assert normaliser('urn:epc:id:gsrnp:4012345.0000000007') == "https://id.gs1.org/8017/401234500000000074"
    assert normaliser('urn:epc:id:gdti:4012345.00009.PO-4711') == "https://id.gs1.org/253/4012345000092PO-4711"
    assert normaliser('urn:epc:id:gdti:987659999999..9') == "https://id.gs1.org/253/98765999999929"
    assert normaliser(
        'urn:epc:id:cpi:0614141.11111111111111-A%23%2F.1234') == "https://id.gs1.org/8010/061414111111111111111-A%23%2F/8011/1234"
    assert normaliser('urn:epc:id:ginc:0614141.xyz47%2F11') == "https://id.gs1.org/401/0614141xyz47%2F11"
    assert normaliser('urn:epc:id:gsin:4012345.222333444') == "https://id.gs1.org/402/40123452223334442"
    assert normaliser('urn:epc:id:itip:4012345.011111.01.02.987') == "https://id.gs1.org/8006/040123451111180102/21/987"
    assert normaliser(
        'urn:epc:id:upui:1234567.098765.51qIgY)%3C%26Jp3*j7SDB') == "https://id.gs1.org/01/01234567987651/235/51qIgY%29%3C%26Jp3%2Aj7SDB"
    assert normaliser('urn:epc:id:pgln:4000001.00000') == "https://id.gs1.org/417/4000001000005"
    assert normaliser('urn:epc:id:pgln:999999999999.') == "https://id.gs1.org/417/9999999999994"
    assert normaliser('urn:epc:class:lgtin:4012345.012345.Lot987') == "https://id.gs1.org/01/04012345123456/10/Lot987"


def test_epc_uri_patterns():
    assert normaliser('urn:epc:idpat:sgtin:4012345.012345.*') == "https://id.gs1.org/01/04012345123456"
    assert normaliser('urn:epc:idpat:grai:4012345.99999.*') == "https://id.gs1.org/8003/04012345999990"
    assert normaliser('urn:epc:idpat:gdti:4012345.11111.*') == "https://id.gs1.org/253/4012345111118"
    assert normaliser('urn:epc:idpat:sgcn:4012345.22222.*') == "https://id.gs1.org/255/4012345222227"
    assert normaliser('urn:epc:idpat:cpi:4012345.AB12.*') == "https://id.gs1.org/8010/4012345AB12"
    assert normaliser('urn:epc:idpat:itip:4012345.012345.01.02.*') == "https://id.gs1.org/8006/040123451234560102"
    assert normaliser('urn:epc:idpat:upui:4012345.012345.*') == "https://id.gs1.org/01/04012345123456"


def test_uris_with_letters_and_ais():
    assert normaliser('https://id.gs1.org/gtin/09780345418913') == "https://id.gs1.org/01/09780345418913"
    assert normaliser(
        'https://example.com/gtin/09780345418913/21/765tz?abc=211121') == "https://id.gs1.org/01/09780345418913/21/765tz"


def test_gtin_8_12_13():
    assert normaliser('http://example.de/gtin-8/01/97803111') == "https://id.gs1.org/01/00000097803111"
    assert normaliser('http://us-company-with-UPC.com/01/001122334455') == "https://id.gs1.org/01/00001122334455"
    assert normaliser(
        'http://us-company-with-UPC.com/01/001122334455/ser/GHB') == "https://id.gs1.org/01/00001122334455/21/GHB"
    assert normaliser(
        'https://ean-13.de/gtin/4012345123456/ser/ABC524') == "https://id.gs1.org/01/04012345123456/21/ABC524"


def test_http_only():
    assert normaliser('http://id.gs1.org/gtin/9780345418913') == "https://id.gs1.org/01/09780345418913"


def test_key_qualifiers():
    assert normaliser(
        'https://id.gs1.org/gtin/9780345418913/cpv/344/lot/1223/ser/765tz') == "https://id.gs1.org/01/09780345418913/21/765tz"
    assert normaliser('https://id.gs1.org/gtin/9780345418913/cpv/344') == "https://id.gs1.org/01/09780345418913"
    assert normaliser(
        'https://example.de/gtin/04012345123456/cpv/344/ser/987654') == "https://id.gs1.org/01/04012345123456/21/987654"
    assert normaliser(
        'http://example.de/01/040123451234/cpv/344/lot/ABD') == "https://id.gs1.org/01/00040123451234/10/ABD"
    assert normaliser(
        'https://id.gs1.org/01/9780345418913/22/344/10/1223/21/765tz') == "https://id.gs1.org/01/09780345418913/21/765tz"
    assert normaliser(
        'https://id.gs1.org/itip/123456789101100190/cpv/ABCD') == "https://id.gs1.org/8006/123456789101100190"
    assert normaliser(
        'https://fashion-corp.com/8006/040123451234560102/22/AB/21/443322') == "https://id.gs1.org/8006/040123451234560102/21/443322"
    assert normaliser(
        'https://id.gs1.org/8006/040123451234560102/22/ABCD/10/XYZ') == "https://id.gs1.org/8006/040123451234560102/10/XYZ"
    assert normaliser(
        'https://fashion-corp.com/8006/040123451234560102/10/Lot-123/21/ser987') == "https://id.gs1.org/8006/040123451234560102/21/ser987"


def test_sub_domains():
    assert normaliser(
        'https://gs1.test.example.org/01/9780345418913/10/1223') == "https://id.gs1.org/01/09780345418913/10/1223"


def test_qualifier_or_custom_data_attributes_in_query_string():
    assert normaliser(
        'https://example.org/01/9780345418913/21/765tz?11=221109') == "https://id.gs1.org/01/09780345418913/21/765tz"
    assert normaliser(
        'https://example.org/01/9780345418913/21/765tz?abc=211121') == "https://id.gs1.org/01/09780345418913/21/765tz"


def test_other_gs1_keys():
    assert normaliser('https://id.gs1.org/00/340123453111111115') == "https://id.gs1.org/00/340123453111111115"
    assert normaliser('https://id.gs1.org/414/4226350800008') == "https://id.gs1.org/414/4226350800008"
    assert normaliser('https://example.co.uk/party/4226350800008') == "https://id.gs1.org/417/4226350800008"
    assert normaliser('https://id.gs1.org/414/4280000000002/254/12') == "https://id.gs1.org/414/4280000000002/254/12"
    assert normaliser('https://id.gs1.org/8003/03870585000552987') == "https://id.gs1.org/8003/03870585000552987"
    assert normaliser('https://id.gs1.org/8004/0180451111ABC987') == "https://id.gs1.org/8004/0180451111ABC987"
    assert normaliser('https://id.gs1.org/8018/385888700111111111') == "https://id.gs1.org/8018/385888700111111111"
    assert normaliser('https://id.gs1.org/8017/440018922222222226') == "https://id.gs1.org/8017/440018922222222226"
    assert normaliser('https://id.gs1.org/253/4602443000331XYZ') == "https://id.gs1.org/253/4602443000331XYZ"
    assert normaliser('https://id.gs1.org/8010/0628165987/8011/9876') == "https://id.gs1.org/8010/0628165987/8011/9876"
    assert normaliser('https://id.gs1.org/255/0811625999996554433') == "https://id.gs1.org/255/0811625999996554433"
    assert normaliser(
        'http://fashion.com/itip/040123451234560102/ser/ABC145') == "https://id.gs1.org/8006/040123451234560102/21/ABC145"


def test_non_existent_key_ai():
    assert normaliser('http://example.org/123/4012345ABC987/456/4711') is None
    assert normaliser('http://id.gs1.org/99/9780345418913') is None
    assert normaliser('http://id.gs1.org/01/9780345418913/99/utfgf') is None


def test_ordinary_web_uri():
    assert normaliser('http://example.de/abc/9780345418913') is None


def test_incorrect_syntax():
    assert normaliser('http://example.de/01/97803') is None
    assert normaliser('https://id.gs1.org/8006/04012345123456/22/ABCD/10/XYZ') is None
    # the following must not throw
    assert normaliser('42') is None
    assert normaliser(42) is None
    assert normaliser('Hello World!') is None
