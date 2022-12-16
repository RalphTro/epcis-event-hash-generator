try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

import xml.etree.ElementTree as ElementTree

from epcis_event_hash_generator.events_from_file_reader import event_list_from_file
from epcis_event_hash_generator.xml_to_py import _xml_to_py


def test_docstring_example():
    xml = """
<obj>
  <a>
    <b>3</b>
    <b>3</b>
    <b>5</b>
    <c e="f"><d>Hello</d><d x="y">World</d></c>
  </a>
  <d>2</d>
</obj>
"""
    expected_obj = [("a", "", [("b", "3", []), ("b", "3", []), ("b", "5", []),
                               ("c", "", [("d", "Hello", []), ("d", "World", [("x", "y", [])]), ("e", "f", [])])]),
                    ("d", "2", [])]

    actual_obj = _xml_to_py(ElementTree.fromstring(xml))

    assert expected_obj == actual_obj[2]


def test_epcsi_reference_example():
    actual_obj = event_list_from_file("examples/ReferenceEventHashAlgorithm.xml")

    print(actual_obj)

    expected_obj = ('EventList', '', [('ObjectEvent', '', [('action', 'OBSERVE', []),
                                                           ('bizStep', 'urn:epcglobal:cbv:bizstep:departing', []), (
                                                               'epcList', '',
                                                               [('epc', 'urn:epc:id:sscc:4012345.0000000111', []),
                                                                ('epc', 'urn:epc:id:sscc:4012345.0000000222', []),
                                                                ('epc', 'urn:epc:id:sscc:4012345.0000000333', [])]),
                                                           ('eventTime', '2020-03-04T11:00:30.000+01:00', []),
                                                           ('eventTimeZoneOffset', '+01:00', []),
                                                           ('readPoint', '',
                                                            [
                                                                ('id',
                                                                 'urn:epc:id:sgln:4012345.00011.987',
                                                                 [])]),
                                                           ('recordTime', '2020-03-04T11:00:30.999+01:00', []), (
                                                               '{https://ns.example.com/epcis/}myField1', '',
                                                               [('{https://ns.example.com/epcis/}mySubField1', '2', []),
                                                                (
                                                                    '{https://ns.example.com/epcis/}mySubField2', '5',
                                                                    [])]),
                                                           ('{https://ns.example.com/epcis/}myField2', '0', []), (
                                                               '{https://ns.example.com/epcis/}myField3', '',
                                                               [('{https://ns.example.com/epcis/}mySubField3', '1', []),
                                                                ('{https://ns.example.com/epcis/}mySubField3', '3',
                                                                 [])])])])

    assert expected_obj == actual_obj
