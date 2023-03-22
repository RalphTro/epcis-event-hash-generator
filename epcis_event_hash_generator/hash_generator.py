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
import copy
import logging
import traceback

import dateutil.parser

try:  # import syntax differs depending on whether this is run as a module or as a script
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.dl_normaliser import normaliser as dl_normaliser
from epcis_event_hash_generator import PROP_ORDER
from epcis_event_hash_generator import JOIN_BY as DEFAULT_JOIN_BY

JOIN_BY = DEFAULT_JOIN_BY


def _fix_time_stamp_format(timestamp):
    """Make sure that the timestamp is given at millisecond precision
    and in UTC."""
    logging.debug("correcting timestamp format for '{}'".format(timestamp))

    try:
        abstract_date_time = dateutil.parser.parse(timestamp)
    except ValueError:
        logging.warning("'%s' is labelled as time but does not match the ISO 8601 dateTime format", timestamp)
        return timestamp

    # convert to UTC
    abstract_date_time = abstract_date_time.astimezone(datetime.timezone.utc)

    microsecond = abstract_date_time.microsecond

    # round off microsecond upto 3 digits
    abstract_date_time = abstract_date_time.replace(microsecond=round(microsecond, -3))

    # normalise precision to ms and convert to ISO string using "Z" instead of +00:00
    fixed = abstract_date_time.isoformat(timespec='milliseconds')[:-6] + "Z"

    logging.debug("corrected timestamp '{}'".format(fixed))
    return fixed


def _child_to_pre_hash_string(child, sub_child_order):
    logging.debug("Processing '%s'", child)
    text = ""
    grand_child_text = ""
    if sub_child_order:
        grand_child_text = _recurse_through_children_in_order(child[2], sub_child_order)
    if child[1]:
        text = child[1].strip()
        if child[0].lower().find("time") >= 0 and child[0].lower().find("offset") < 0:
            text = _fix_time_stamp_format(text)
        else:
            text = _canonize_value(text)

        if text:
            text = "=" + text

    if text or grand_child_text:
        re = child[0] + text + grand_child_text
        logging.debug("pre hash string element: '%s'", text)
        return re

    return ""


def _recurse_through_children_in_order(child_list, child_order):
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

    user_extensions = _gather_user_extensions(child_list)

    for (child_name, sub_child_order) in child_order:
        children = [x for x in child_list if x[0] == child_name]  # elements with the same name
        list_of_values = []

        for child in children:
            child_pre_hash = _child_to_pre_hash_string(child, sub_child_order)
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

    if len(user_extensions) > 0:
        user_extensions_prehash = _generic_child_list_to_prehash_string(user_extensions)
        pre_hash = pre_hash + JOIN_BY + user_extensions_prehash

    logging.debug("child list pre hash is %s", pre_hash)

    return pre_hash


def _canonize_value(text):
    """Run a value through all format canonizations"""
    text = _try_format_web_vocabulary(text)
    text = _try_format_numeric(text)
    converted = dl_normaliser(text)
    if converted:
        logging.debug("Converted %s to %s", text, converted)
        return converted
    logging.debug("No canonical form for '%s'", text)
    return text


def _gather_user_extensions(child_list):
    """
    Collect user extensions enclosed in child like sensorElementList, readPoint, etc.
    So that user extensions can be appended to its enclosing element only
    """
    user_extensions = []

    if len(child_list) <= 1:
        return user_extensions

    # ignore top level user extensions
    for child in child_list:
        if 'eventTime' in child[0] or 'action' in child[0]:
            return user_extensions

    # collect user extensions in a separate list
    for x in child_list:
        if isinstance(x, tuple) and ('{' in x[0] and '/}' in x[0]):
            user_extensions.append(x)

    # remove user extensions from original list
    if user_extensions:
        for element_to_remove in user_extensions:
            child_list.remove(element_to_remove)

    return user_extensions


def _try_format_web_vocabulary(text):
    """Replace old CBV URNs by new web vocabulary equivalents."""
    return text.replace(
        'urn:epcglobal:cbv:bizstep:', 'https://ref.gs1.org/cbv/BizStep-'
    ).replace(
        'urn:epcglobal:cbv:disp:', 'https://ref.gs1.org/cbv/Disp-'
    ).replace(
        'urn:epcglobal:cbv:btt:', 'https://ref.gs1.org/cbv/BTT-'
    ).replace(
        'urn:epcglobal:cbv:sdt:', 'https://ref.gs1.org/cbv/SDT-'
    ).replace('urn:epcglobal:cbv:er:', 'https://ref.gs1.org/cbv/ER-')


def _try_format_numeric(text):
    """remove leading/trailing zeros, leading "+", etc. from numbers. Non numeric values are left untouched."""
    try:
        numeric = float(text)
        if int(numeric) == numeric:  # remove trailing .0
            numeric = int(numeric)
        text = str(numeric)
    except ValueError:
        pass
    return text


def _generic_child_list_to_prehash_string(children):
    list_of_values = []

    logging.debug("Parsing remaining elements in: %s", children)

    for child in children:
        if isinstance(child, tuple) and len(child) == 2 and isinstance(child[0], tuple):
            list_of_values.append(_generic_child_list_to_prehash_string(child))
        else:
            text = child[1].strip()
            if text:
                text = _canonize_value(text)
                text = "=" + text
            list_of_values.append(child[0] + text + _generic_child_list_to_prehash_string(child[2]))

    if len(children) > 1 and should_sort(children):
        list_of_values.sort()
    return JOIN_BY.join(list_of_values)


def should_sort(children):
    """
    avoid sort for 'bizTransaction', 'source', 'destination' to match order as defined in CBV 2.0
    :param children:
    :return: True/False
    """
    for child in children:
        if child[0] == 'bizTransaction' or child[0] == 'source' or child[0] == 'destination':
            return False
    return True


def _gather_elements_not_in_order(children, child_order):
    """
    Collects vendor extensions not covered by the defined child order. Consumes the root.
    """

    # remove fields that are to be ignored in the hash:
    # remove all elements from XML tree which do shouldn't take part in hash calculation
    to_be_ignored = ["recordTime", "eventID", "type", "errorDeclaration"]
    children = [child for child in children if child[0] not in to_be_ignored]
    if children:
        return _generic_child_list_to_prehash_string(children)

    return ""


def derive_prehashes_from_events(events, join_by=DEFAULT_JOIN_BY):
    """
    Compute a normalized form (pre-hash string) for each event.
    This is the main functionality of the hash generator.
    """

    events = copy.deepcopy(events)  # do not change parameter!

    global JOIN_BY
    join_by = join_by.replace(r"\n", "\n").replace(r"\t", "\t")
    logging.debug("Setting JOIN_BY='%s'", join_by)
    JOIN_BY = join_by

    logging.info("#events = %s", len(events[2]))
    for i in range(len(events[2])):
        logging.info("%s: %s\n", i, events[2][i])

    prehash_string_list = []
    for event in events[2]:
        logging.debug("prehashing event:\n%s", event)
        try:
            prehash_string_list.append("eventType=" + event[0] + JOIN_BY
                                       + _recurse_through_children_in_order(event[2], PROP_ORDER) + JOIN_BY
                                       + _gather_elements_not_in_order(event[2], PROP_ORDER)
                                       )
        except Exception as ex:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, ex)
            logging.debug("".join(traceback.format_tb(ex.__traceback__)))
            pass

    # To see/check concatenated value string before hash algorithm is performed:
    logging.debug("prehash_string_list = {}".format(prehash_string_list))
    return prehash_string_list


def calculate_hashes_from_pre_hashes(prehash_string_list, hashalg="sha256"):
    """Hash all strings in the list with the given algorithm. Returned in the appropriate NI format.
    """
    hashValueList = []
    for pre_hash_string in prehash_string_list:
        if hashalg == 'sha256':
            hash_string = 'ni:///sha-256;' + \
                          hashlib.sha256(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha3-256':
            hash_string = 'ni:///sha3-256;' + \
                          hashlib.sha3_256(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha384':
            hash_string = 'ni:///sha-384;' + \
                          hashlib.sha384(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        elif hashalg == 'sha512':
            hash_string = 'ni:///sha-512;' + \
                          hashlib.sha512(pre_hash_string.encode('utf-8')).hexdigest() + '?ver=CBV2.0'
        else:
            raise ValueError("Unsupported Hashing Algorithm: " + hashalg)

        hashValueList.append(hash_string)

    return hashValueList


def epcis_hashes_from_events(events, hashalg="sha256"):
    """Calculate the list of hashes from the given events list
    + hashing algorithm through the pre hash string using default parameters.
    """
    prehash_string_list = derive_prehashes_from_events(events)
    return calculate_hashes_from_pre_hashes(prehash_string_list, hashalg)
