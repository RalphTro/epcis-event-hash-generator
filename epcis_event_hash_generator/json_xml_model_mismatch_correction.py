"""Correct the missmatch of EPCIS 2.0 XML and JSON data models, taking a JSON and producing the XML model.

For example
{
  "type": "ObjectEvent",
  "eventTime": "2019-04-02T15:00:00.000+01:00",
  "eventTimeZoneOffset": "+01:00",
  "epcList": [
    "urn:epc:id:sgtin:4012345.011111.9876",
"urn:epc:id:sgtin:4012345.011111.5432"
  ],
  "action": "OBSERVE",
}

is converted to

("ObjectEvent","",[
  ("eventTime","2019-04-02T15:00:00.000+01:00", []),
  ("eventTimeZoneOffset","+01:00", []),
  ("epcList", "", [
    ("epc", "urn:epc:id:sgtin:4012345.011111.5432", []),
    ("epc", "urn:epc:id:sgtin:4012345.011111.9876", [])
  ],
  ("action", "OBSERVE", [])
])


.. module:: json_xml_model_mismatch_correction

.. moduleauthor:: Sebastian Schmittner <schmittner@eecc.info>

Copyright 2020 Ralph Troeger, Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""


def _correct_xml_vs_js_structure_mismatch(py_obj):
    """
    Some of the object substructure in XML EPCIS is just not present in JSON or unsystematically renamed
    """

    # inconsistent child names / omissions
    if py_obj[0] == "inputEPC" or py_obj[0] == "outputEPC":
        return "epc", py_obj[1], py_obj[2]

    # quantity can be a quantityList child which should be called quantityElement (omitted in JSON) or the quantity
    # property of such an element
    if py_obj[0] == "inputQuantity" or py_obj[0] == "outputQuantity" or py_obj[0] == "childQuantity" or (
            py_obj[0] == "quantity" and len(py_obj[2]) > 0):
        return "quantityElement", py_obj[1], py_obj[2]

    if py_obj[0] == "inputQuantity" or py_obj[0] == "outputQuantity":
        return "quantityElement", py_obj[1], py_obj[2]

    return py_obj


def deep_structure_correction(py_obj):
    """deep copy, applying structure corrections"""

    lvl1_corrected_children = []
    if len(py_obj) > 2:
        lvl1_corrected_children = py_obj[2]

    # Systematic correction of elementList child name omissions
    lists = {}
    for element in [e for e in lvl1_corrected_children if not isinstance(e[0], tuple) and e[0].endswith("List")]:
        if not element[0] in lists:
            lists[element[0]] = []
        lists[element[0]].append((element[0][:-4], element[1], element[2]))
        lvl1_corrected_children.remove(element)

    for list_name, list_elements in lists.items():
        if list_name in ["sourceList", "destinationList", "bizTransactionList"]:
            lvl1_corrected_children.append((list_name, "", list(map(lambda e: (e[2][0], e[2][1]), list_elements))))
        else:
            lvl1_corrected_children.append((list_name, "", list_elements))

    # list of childEPCs -> childEPCs list of EPCs
    child_epcs = []
    for element in [element for element in lvl1_corrected_children if element[0] == "childEPCs"]:
        child_epcs.append(("epc", element[1], []))
        lvl1_corrected_children.remove(element)

    if child_epcs:
        lvl1_corrected_children.append(("childEPCs", "", child_epcs))

    corrected_children = []
    # recursion
    for element in lvl1_corrected_children:
        # no need to do recursion for elements with no second level
        if element[0] in ["sourceList", "destinationList", "bizTransactionList"]:
            corrected_children.append(element)
        else:
            corrected_children.append(deep_structure_correction(element))

    # 2nd level corrections
    return _correct_xml_vs_js_structure_mismatch((py_obj[0], py_obj[1], corrected_children))
