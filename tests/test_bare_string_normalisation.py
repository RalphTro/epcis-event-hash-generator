try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.events_from_file_reader import event_list_from_file


def test_epcsi_reference_example():
    actual_obj = event_list_from_file("examples/epcisDocWithSingleEvent.jsonld")

    print(actual_obj)

    expected_obj = ('EventList', '', [
        ('ObjectEvent', '', [
            ('action', 'OBSERVE', []),
            ('bizStep', 'https://ref.gs1.org/cbv/BizStep-shipping', []),
            ('disposition', 'https://ref.gs1.org/cbv/Disp-in_transit', []),
            ('eventTime', '2022-02-16T20:33:31.116000-06:00', []),
            ('eventTimeZoneOffset', '-06:00', []),
            ('readPoint', '', [
                ('id', 'urn:epc:id:sgln:0614141.07346.1234', [])
            ]),
            ('type', 'ObjectEvent', []),
            ('bizTransactionList', '', [
                (('type', 'https://ref.gs1.org/cbv/BTT-po', []),
                 ('bizTransaction', 'http://transaction.acme.com/po/12345678', []))
            ]),
            ('epcList', '', [
                ('epc', 'urn:epc:id:sgtin:0614141.107346.2017', []),
                ('epc', 'urn:epc:id:sgtin:0614141.107346.2018', [])
            ])
        ])])

    assert expected_obj == actual_obj
