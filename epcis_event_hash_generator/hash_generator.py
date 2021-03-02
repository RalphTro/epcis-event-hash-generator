"""This is a prove of concept implementation of an algorithm to calculate a hash of EPCIS events.

.. module:: hash_generator
   :synopsis: Calculates the EPCIS event hash as specified in https://github.com/RalphTro/epcis-event-hash-generator/

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>, Sebastian Schmittner <schmittner@eecc.info>

Copyright 2019-2021 Ralph Troeger, Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

import datetime
import hashlib
import logging
import traceback

import dateutil.parser

try:  # import syntax differs depending on whether this is run as a module or as a script
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.dl_normaliser import normaliser as dl_normaliser
from epcis_event_hash_generator.xml_to_py import event_list_from_epcis_document_xml as read_xml
from epcis_event_hash_generator.xml_to_py import event_list_from_epcis_document_xml_str as read_xml_str
from epcis_event_hash_generator.json_to_py import event_list_from_epcis_document_json as read_json
from epcis_event_hash_generator.json_to_py import event_list_from_epcis_document_json_str as read_json_str
from epcis_event_hash_generator import PROP_ORDER
from epcis_event_hash_generator import JOIN_BY as DEFAULT_JOIN_BY

JOIN_BY = DEFAULT_JOIN_BY


def fix_time_stamp_format(timestamp):
    """Make sure that the timestamp is given at millisecond precision
    and in UTC."""
    logging.debug("correcting timestamp format for '{}'".format(timestamp))

    try:
        abstract_date_time = dateutil.parser.parse(timestamp)
    except ValueError:
        logging.warning("'{}' is labelled as time but does not match the ISO 8601 dateTime format", timestamp)
        return timestamp

    # convert to UTC
    abstract_date_time = abstract_date_time.astimezone(datetime.timezone.utc)
    # normalise precision to ms and convert to ISO string using "Z" instead of +00:00
    fixed = abstract_date_time.isoformat(timespec='milliseconds')[:-6] + "Z"

    logging.debug("corrected timestamp '{}'".format(fixed))
    return fixed


def child_to_pre_hash_string(child, sub_child_order):
    text = ""
    grand_child_text = ""
    if sub_child_order:
        grand_child_text = recurse_through_children_in_order(child[2], sub_child_order)
    if child[1]:
        text = child[1].strip()
        if child[0].lower().find("time") > 0 and child[0].lower().find("offset") < 0:
            text = fix_time_stamp_format(text)
        else:
            text = canonize_value(text)

        if text:
            text = "=" + text
            logging.debug("Adding text '%s'", text)

    if text or grand_child_text:
        return child[0] + text + grand_child_text

    return ""


def recurse_through_children_in_order(child_list, child_order):
    """
    Loop over child order, look for a child of root with matching key and build the pre-hash string (mostly key=value)
    Recurse through the grand children applying the sub order.
    All elements added to the returned pre hash string are removed from the tree below the root.
    After the recursion completes, only elements NOT added to the pre-hash string are left in the tree.

    `child_list`    is to be a list of simple python object, i.e. triples of two strings (key/value) and a list of
                    simple python objects (grand children).
    `child_order`   is expected to be a property order, see PROP_ORDER.

    """
    pre_hash = ""
    logging.debug("Calculating pre hash for child list %s \nWith order %s", child_list, child_order)
    for (child_name, sub_child_order) in child_order:
        children = [x for x in child_list if x[0] == child_name]  # elements with the same name
        list_of_values = []

        for child in children:
            child_pre_hash = child_to_pre_hash_string(child, sub_child_order)
            if child_pre_hash:
                list_of_values.append(child_pre_hash)
            else:
                logging.debug("Empty element ignored: %s", child)

            if len(child[2]) == 0:
                logging.debug("Finished processing %s", child)
                child_list.remove(child)

        # sort list of values to fix #10
        list_of_values.sort()

        if "".join(list_of_values):  # fixes #16
            if pre_hash:
                list_of_values.insert(0, pre_hash)  # yields correct Joining behavior
            pre_hash = JOIN_BY.join(list_of_values)

    logging.debug("child list pre hash is %s", pre_hash)

    return pre_hash


def canonize_value(text):
    """Run a value through all format canonizations"""
    text = try_format_web_vocabulary(text)
    text = try_format_numeric(text)
    converted = dl_normaliser(text)
    if converted:
        logging.debug("Converted %s to %s", text, converted)
        return converted
    return text


def try_format_web_vocabulary(text):
    """Replace old CBV URNs by new web vocabulary equivalents."""
    return text.replace(
        'urn:epcglobal:cbv:bizstep:', 'https://ns.gs1.org/voc/Bizstep-'
    ).replace(
        'urn:epcglobal:cbv:disp:', 'https://ns.gs1.org/voc/Disp-'
    ).replace(
        'urn:epcglobal:cbv:btt:', 'https://ns.gs1.org/voc/BTT-'
    ).replace(
        'urn:epcglobal:cbv:sdt:', 'https://ns.gs1.org/voc/SDT-'
    ).replace('urn:epcglobal:cbv:er:', 'https://ns.gs1.org/voc/ER-')


def try_format_numeric(text):
    """remove leading/trailing zeros, leading "+", etc. from numbers. Non numeric values are left untouched."""
    try:
        numeric = float(text)
        if int(numeric) == numeric:  # remove trailing .0
            numeric = int(numeric)
        text = str(numeric)
    except ValueError:
        pass
    return text


def generic_child_list_to_prehash_string(children):
    list_of_values = []

    logging.debug("Parsing remaining elements in: %s", children)

    for child in children:
        text = child[1].strip()
        if text:
            text = canonize_value(text)
            text = "=" + text
        list_of_values.append(child[0] + text + generic_child_list_to_prehash_string(child[2]))

    list_of_values.sort()
    return JOIN_BY.join(list_of_values)


def gather_elements_not_in_order(children, child_order):
    """
    Collects vendor extensions not covered by the defined child order. Consumes the root.
    """

    # remove fields that are to be ignored in the hash:
    # remove all elements from XML tree which do shouldn't take part in hash calculation
    to_be_ignored = ["recordTime", "eventID"]
    for child in children:
        if child[0] in to_be_ignored:
            children.remove(child)
    if children:
        return generic_child_list_to_prehash_string(children)

    return ""


def compute_prehash_from_file(path, enforce=None):
    """Read EPCIS document and generate pre-hash strings.
    Use enforce = "XML" or "JSON" to ignore file ending and use JSON/XML parser.
    """
    if enforce == "XML" or path.lower().endswith(".xml"):
        events = read_xml(path)
    elif enforce == "JSON" or path.lower().endswith(".json") or path.lower().endswith(".jsonld"):
        events = read_json(path)
    else:
        logging.error("Filename '%s' ending not recognized.", path)
        return None

    return compute_prehash_from_events(events)


def compute_prehash_from_json_str(jsonStr):
    """Read EPCIS document and generate pre-hash strings.
    Use enforce = "XML" or "JSON" to ignore file ending.
    """

    events = read_json_str(jsonStr)

    return compute_prehash_from_events(events)


def compute_prehash_from_xml_str(xmlStr):
    """Read EPCIS document and generate pre-hash strings.
    Use enforce = "XML" or "JSON" to ignore file ending.
    """
    events = read_xml_str(xmlStr.decode("utf-8"))
    return compute_prehash_from_events(events)


def compute_prehash_from_events(events):
    logging.info("#events = %s", len(events[2]))
    for i in range(len(events[2])):
        logging.info("%s: %s\n", i, events[2][i])

    prehash_string_list = []
    for event in events[2]:
        logging.debug("prehashing event:\n%s", event)
        try:
            prehash_string_list.append("eventType=" + event[0] + JOIN_BY
                                       + recurse_through_children_in_order(event[2], PROP_ORDER) + JOIN_BY
                                       + gather_elements_not_in_order(event[2], PROP_ORDER)
                                       )
        except Exception as ex:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, ex)
            logging.debug("".join(traceback.format_tb(ex.__traceback__)))
            pass

    # To see/check concatenated value string before hash algorithm is performed:
    logging.debug("prehash_string_list = {}".format(prehash_string_list))
    return prehash_string_list


def epcis_hash_from_json(json, hashalg="sha256"):
    prehash_string_list = compute_prehash_from_json_str(json)
    return calculate_hash(prehash_string_list, hashalg)


def epcis_hash_from_xml(xmlStr, hashalg="sha256"):
    prehash_string_list = compute_prehash_from_xml_str(xmlStr)
    return calculate_hash(prehash_string_list, hashalg)


def epcis_hash(path, hashalg="sha256", join_by=DEFAULT_JOIN_BY):
    """Read all EPCIS Events from the EPCIS XML document at path.
    Compute a normalized form (pre-hash string) for each event and
    return an array of the event hashes computed from the pre-hash by
    hashalg.
    """
    global JOIN_BY
    join_by = join_by.replace(r"\n", "\n").replace(r"\t", "\t")
    logging.debug("Setting JOIN_BY='%s'", join_by)
    JOIN_BY = join_by
    prehash_string_list = compute_prehash_from_file(path)

    return calculate_hash(prehash_string_list, hashalg)


def calculate_hash(prehash_string_list, hashalg="sha256"):
    hashValueList = []
    for pre_hash_string in prehash_string_list:
        if hashalg == 'sha256':
            hash_string = 'ni:///sha-256;' + \
                          hashlib.sha256(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha3_256':
            hash_string = 'ni:///sha3_256;' + \
                          hashlib.sha3_256(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha384':
            hash_string = 'ni:///sha-384;' + \
                          hashlib.sha384(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha512':
            hash_string = 'ni:///sha-512;' + \
                          hashlib.sha512(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        else:
            raise ValueError("Unsupported Hashing Algorithm: " + hash_string)

        hashValueList.append(hash_string)

    return hashValueList, prehash_string_list
