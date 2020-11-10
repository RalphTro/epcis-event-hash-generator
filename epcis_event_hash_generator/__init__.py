# -*- coding: utf-8 -*-

PROP_ORDER = [
    ('eventTime', None),
    ('eventTimeZoneOffset', None),
    ('errorDeclaration',
     [
         ('declarationTime', None),
         ('reason', None),
         ('correctiveEventIDs', [('correctiveEventID', None)])
     ]),
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
    ('readPoint', [('id', None)]),
    ('bizLocation', [('id', None)]),
    ('bizTransactionList', [('bizTransaction', [('type', None)])]),
    ('sourceList', [('source', [('type', None)])]),
    ('destinationList', [('destination', [('type', None)])]),
    ('sensorElementList', [('sensorElement',
                            [('sensorMetaData',
                              [
                                  ('time', None),
                                  ('startTime', None),
                                  ('endTime', None),
                                  ('deviceID', None),
                                  ('deviceMetaData', None),
                                  ('rawData', None),
                                  ('dataProcessingMethod', None),
                                  ('bizRules', None)
                              ]),  # end sensorMetaData
                             ('sensorReport',
                              [
                                  ('type', None),
                                  ('deviceID', None),
                                  ('deviceMetaData', None),
                                  ('rawData', None),
                                  ('dataProcessingMethod', None),
                                  ('microorganism', None),
                                  ('chemicalSubstance', None),
                                  ('value', None),
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
