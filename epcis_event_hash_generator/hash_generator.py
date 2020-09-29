"""This is a prove of concept implementation of an algorithm to calculate a hash of EPCIS events.

.. module:: hash_generator
   :synopsis: Calculates the EPCIS event hash as specified in https://github.com/RalphTro/epcis-event-hash-generator/

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>, Sebastian Schmittner <schmittner@eecc.info>

Copyright 2019-2020 Ralph Troeger, Sebastian Schmittner

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

import dateutil.parser

try:  # import syntax differs depending on whether this is run as a module or as a script
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.xml_to_py import event_list_from_epcis_document_xml as read_xml
from epcis_event_hash_generator.json_to_py import event_list_from_epcis_document_json as read_json
from epcis_event_hash_generator import PROP_ORDER


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


def recurse_through_children_in_order(root, child_order):
    """child_order is expected to be a property order, see PROP_ORDER. Loop over child order, look for a child of
    root with matching name and add its text (if any). Recurse through the grand children applying the sub order.
    """
    texts = ""
    for (child_name, sub_child_order) in child_order:
        list_of_values = []
        prefix = ""
        for child in [x for x in root if x[0] == child_name]:
            if sub_child_order:
                list_of_values.append(recurse_through_children_in_order(child[2], sub_child_order))
                prefix = child_name
            if child[1]:
                text = child[1].strip()
                if child_name.lower().find("time") > 0 and child_name.lower().find("offset") < 0:
                    text = fix_time_stamp_format(text)
                else:
                    text = format_if_numeric(text)

                logging.debug("Adding text '%s'", text)
                list_of_values.append(
                    child_name + "=" + text)

        # sort list of values to fix !10
        list_of_values.sort()
        if len(list_of_values) > 1:
            logging.debug("sorted: %s", list_of_values)

        if "".join(list_of_values):  # fixes #16
            texts += prefix + "".join(list_of_values)
        elif prefix:
            logging.debug("Skipping empty element: %s", prefix)
    return texts


def format_if_numeric(text):
    """remove leading/trailing zeros, leading "+", etc. from numbers"""
    try:
        numeric = float(text)
        if int(numeric) == numeric:  # remove trailing .0
            numeric = int(numeric)
        text = str(numeric)
    except ValueError:
        pass
    return text


def generic_element_to_prehash_string(root):
    list_of_values = []

    logging.debug("Parsing remaining elements: %s", root)
    if isinstance(root, str) and root:
        list_of_values.append("=" + root.strip())
    else:
        for child in root:
            list_of_values.append(child[0] + generic_element_to_prehash_string(
                child[1]) + generic_element_to_prehash_string(child[2]))

    list_of_values.sort()
    return "".join(list_of_values)


def gather_elements_not_in_order(root, child_order):
    """
    Collects vendor extensions not covered by the defined child order. Consumes the root.
    """

    # remove recordTime, if any
    child_order_or_record_time = child_order + [("recordTime", None)]

    for (child_name, _) in child_order_or_record_time:
        covered_children = [x for x in root if x[0] == child_name]
        logging.debug("Children '%s' covered by ordering: %s", child_name, covered_children)
        for child in covered_children:
            root.remove(child)

    logging.debug("Parsing remaining elements in: %s", root)
    if root:
        return generic_element_to_prehash_string(root)

    return ""


def compute_prehash_from_file(path, enforce=None):
    """Read EPCIS document and generate pre-hashe strings.
    Use enforce = "XML" or "JSON" to ignore file ending.
    """
    if enforce == "XML" or path.lower().endswith(".xml"):
        events = read_xml(path)
    elif enforce == "JSON" or path.lower().endswith(".json"):
        events = read_json(path)
    else:
        logging.error("Filename '%s' ending not recognized.", path)

    logging.info("#events = %s", len(events[2]))
    for i in range(len(events[2])):
        logging.info("%s: %s\n", i, events[2][i])

    prehash_string_list = []
    for event in events[2]:
        logging.debug("prehashing event:\n%s", event)
        try:
            prehash_string_list.append("eventType=" + event[0] +
                                       recurse_through_children_in_order(event[2], PROP_ORDER)
                                       + gather_elements_not_in_order(event[2], PROP_ORDER)
                                       )
        except Exception as ex:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, ex)
            pass

    # To see/check concatenated value string before hash algorithm is performed:
    logging.debug("prehash_string_list = {}".format(prehash_string_list))

    return prehash_string_list


def epcis_hash(path, hashalg="sha256"):
    """Read all EPCIS Events from the EPCIS XML document at path.
    Compute a normalized form (pre-hash string) for each event and
    return an array of the event hashes computed from the pre-hash by
    hashalg.
    """
    prehash_string_list = compute_prehash_from_file(path)

    # Calculate hash values and prefix them according to RFC 6920
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

    return (hashValueList, prehash_string_list)
