# -*- coding: utf-8 -*-

from pyld import jsonld

try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator import file_document_loader


JOIN_BY = ""
"""
Join the substrings to the pre hash string using this deliminator.
By the specification in https://github.com/RalphTro/epcis-event-hash-generator this is to be the empty string,
but using e.g. newline might be helpful for debugging.
When using the command line utility, this can be changed via the -j flag.
"""

PROP_ORDER = [
    ('eventTime', None),
    ('eventTimeZoneOffset', None),
    ('certificationInfo', None),
    ('parentID', None),
    ('epcList', [('epc', None)]),
    ('inputEPCList', [('epc', None)]),
    ('childEPCs', [('epc', None)]),
    ('quantityList', [('quantityElement',
                       [
                           ('epcClass', None),
                           ('quantity', None),
                           ('uom', None)
                       ])]),
    ('childQuantityList', [('quantityElement',
                            [
                                ('epcClass', None),
                                ('quantity', None),
                                ('uom', None)
                            ])
                           ]),
    ('inputQuantityList', [('quantityElement',
                            [
                                ('epcClass', None),
                                ('quantity', None),
                                ('uom', None)
                            ])]),
    ('outputEPCList', [('epc', None)]),
    ('outputQuantityList', [('quantityElement',
                             [
                                 ('epcClass', None),
                                 ('quantity', None),
                                 ('uom', None)
                             ])]),
    ('action', None),
    ('transformationID', None),
    ('bizStep', None),
    ('disposition', None),
    ('persistentDisposition', [
        ('set', None),
        ('unset', None)
    ]),
    ('readPoint', [('id', None)]),
    ('bizLocation', [('id', None)]),

    ('bizTransactionList', [(('type', None), ('bizTransaction', None))]),
    ('sourceList', [(('type', None), ('source', None))]),
    ('destinationList', [(('type', None), ('destination', None))]),
    ('sensorElementList', [('sensorElement',
                            [('sensorMetadata',
                              [
                                  ('time', None),
                                  ('startTime', None),
                                  ('endTime', None),
                                  ('deviceID', None),
                                  ('deviceMetadata', None),
                                  ('rawData', None),
                                  ('dataProcessingMethod', None),
                                  ('bizRules', None)
                              ]),  # end sensorMetadata
                             ('sensorReport',
                              [
                                  ('type', None),
                                  ('exception', None),
                                  ('deviceID', None),
                                  ('deviceMetadata', None),
                                  ('rawData', None),
                                  ('dataProcessingMethod', None),
                                  ('time', None),
                                  ('microorganism', None),
                                  ('chemicalSubstance', None),
                                  ('value', None),
                                  ('component', None),
                                  ('stringValue', None),
                                  ('booleanValue', None),
                                  ('hexBinaryValue', None),
                                  ('uriValue', None),
                                  ('minValue', None),
                                  ('maxValue', None),
                                  ('meanValue', None),
                                  ('sDev', None),
                                  ('percRank', None),
                                  ('percValue', None),
                                  ('uom', None),
                                  ('coordinateReferenceSystem', None)
                              ])  # end sensorReport
                             ])])  # end sensorElement
]
"""The property order data structure describes the ordering in which
to concatenate the contents of an EPCIS event. It is a list
of pairs. The first part of each pair is a string, naming the xml
element. If the element might have children whose order needs to be
defined, the second element is a property order for the children,
otherwise the second element is None.

"""


jsonld.set_document_loader(file_document_loader.file_document_loader())
