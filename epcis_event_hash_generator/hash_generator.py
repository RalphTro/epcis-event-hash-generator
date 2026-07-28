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
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

try:  # import syntax differs depending on whether this is run as a module or as a script
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

from epcis_event_hash_generator.dl_normaliser import normaliser as dl_normaliser
from epcis_event_hash_generator import PROP_ORDER
from epcis_event_hash_generator import JOIN_BY as DEFAULT_JOIN_BY
from epcis_event_hash_generator.cbv_version import profile_for # version-specific behaviour flags

JOIN_BY = DEFAULT_JOIN_BY

# Default CBV version for hash generation
DEFAULT_CBV_VERSION = "CBV2.0"


def _fix_time_stamp_format(timestamp, cbv_version=DEFAULT_CBV_VERSION):
    """Express the timestamp in UTC at millisecond precision (CBV rule 9).
    More than 3 fractional digits are rounded HALF-UP to 3 (.1415 -> .142, .1414 -> .141);
    fewer are zero-filled to 3 (.1 -> .100, none -> .000). This is identical for CBV2.0 and
    CBV2.1 (2.1 only states the rounding explicitly), so there is no version branch here."""
    logging.debug("correcting timestamp format for '{}' ".format(timestamp))

    try:
        # parse any ISO-8601 form
        abstract_date_time = dateutil.parser.parse(timestamp)
    except ValueError:
        logging.warning("'%s' is labelled as time but does not match the ISO 8601 dateTime format", timestamp)
        return timestamp

    # normalise to UTC
    abstract_date_time = abstract_date_time.astimezone(datetime.timezone.utc)

    # Rule 9: express at millisecond precision. Round any excess digits HALF-UP to 3
    millis = int((Decimal(abstract_date_time.microsecond) / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    # Rebuild via timedelta so a 999 -> 1000 ms carry rolls the seconds up correctly
    fixed_dt = abstract_date_time.replace(microsecond=0) + datetime.timedelta(milliseconds=millis)

    # +00:00 -> Z, always 3 digits
    fixed = fixed_dt.isoformat(timespec="milliseconds")[:-6] + "Z"

    logging.debug("corrected timestamp '{}' -> '{}'".format(timestamp, fixed))
    return fixed

def _child_to_pre_hash_string(child, sub_child_order, cbv_version=DEFAULT_CBV_VERSION):
    logging.debug("Processing '%s'", child)
    text = ""
    grand_child_text = ""
    if sub_child_order:
        if child[2] and all(isinstance(gc, tuple) and len(gc) == 2 and isinstance(gc[0], tuple) for gc in child[2]):
        # bizTransactionList/sourceList/destinationList (type, value)  serialize them here (CBV rule #20/#21/#22)
            grand_child_text = _generic_child_list_to_prehash_string(child[2])
            child[2].clear()
        else:
            grand_child_text = _recurse_through_children_in_order(child[2], sub_child_order, cbv_version)
    if child[1]:
        text = child[1].strip()
        if child[0].lower().find("time") >= 0 and child[0].lower().find("offset") < 0:
            text = _fix_time_stamp_format(text, cbv_version)
        else:
            text = _canonize_value(text)

        if text:
            text = "=" + text

    if text or grand_child_text:
        name = child[0]
        # CBV property order #23: 2.0 has no "sensorElementList" wrapper and 2.1 includes it
        if name == "sensorElementList" and not profile_for(cbv_version).keep_sensor_element_list:
            name = ""
        re = name + text
        if grand_child_text:
            # JOIN_BY is "" for the hash; display only
            re += (JOIN_BY if re else "") + grand_child_text
        logging.debug("pre hash string element: '%s'", text)
        return re

    return ""


def _recurse_through_children_in_order(child_list, child_order, cbv_version=DEFAULT_CBV_VERSION):
    """
    Loop over child order, look for a child of root with matching key and build the pre-hash string (mostly key=value)
    Recurse through the grand children applying the sub order.
    All elements added to the returned pre hash string are removed from the tree below the root.
    After the recursion completes, only elements NOT added to the pre-hash string are left in the tree.

    `child_list`    is to be a list of simple python object, i.e. triples of two strings (key/value) and a list of
                    simple python objects (grand children).
    `child_order`   is expected to be a property order, see PROP_ORDER.
    `cbv_version`   is the CBV version to use for timestamp processing.

    """
    pre_hash = ""
    logging.debug("Calculating pre hash for child list %s \nWith order %s", child_list, child_order)

    user_extensions = _gather_user_extensions(child_list, cbv_version)

    for (child_name, sub_child_order) in child_order:
        children = [x for x in child_list if x[0] == child_name]  # elements with the same name
        list_of_values = []

        for child in children:
            child_pre_hash = _child_to_pre_hash_string(child, sub_child_order, cbv_version)
            if child_pre_hash:
                list_of_values.append(child_pre_hash)
            else:
                logging.debug("Empty element ignored: %s", child)

            if len(child[2]) == 0:
                logging.debug("Finished processing %s", child)
                child_list.remove(child)

        # sort list of values to fix #10
        # sort by the canonical (without using any join by character) so the displayed order pre-hash string
        list_of_values.sort(key=lambda v: v.replace(JOIN_BY, "") if JOIN_BY else v)

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


def _gather_user_extensions(child_list, cbv_version=DEFAULT_CBV_VERSION):
    """
    Collect user extensions enclosed in child like sensorElementList, readPoint, etc.
    So that user extensions can be appended to its enclosing element only
    """
    user_extensions = []

    # CBV2.0 does not inline extensions inside standard fields; they are added to the end of the block (see _field_extensions). Only CBV2.1 inlines them here.
    if not profile_for(cbv_version).inline_user_extensions:
        return user_extensions

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
        # if number return exact number float loses precision on big values
        numeric = Decimal(text)
    except InvalidOperation:
        # not a number -> leave unchanged
        return text
    if not numeric.is_finite():
        return text
    if numeric == numeric.to_integral_value():
        # whole number -> plain integer,
        return str(numeric.to_integral_value())
    return format(numeric.normalize(), 'f')


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
            entry = child[0] + text
            grand = _generic_child_list_to_prehash_string(child[2])
            if grand:
                # JOIN_BY is "" for the hash; display only
                entry += (JOIN_BY if entry else "") + grand
            list_of_values.append(entry)

    if len(children) > 1 and should_sort(children):
        list_of_values.sort(key=lambda v: v.replace(JOIN_BY, "") if JOIN_BY else v)
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
    # certificationInfo is not in the CBV canonical property order, so it must never be hashed
    to_be_ignored = ["recordTime", "eventID", "type", "errorDeclaration", "certificationInfo"]
    children = [child for child in children if child[0] not in to_be_ignored]
    if children:
        return _generic_child_list_to_prehash_string(children)

    return ""

def _field_extensions(children, child_order, cbv_version, include_direct=True):
    """CBV2.0 (rule 20): user extensions inside standard fields with extension points are emitted
    in a trailing block, prefixed by their standard field-name path. Walk the standard fields in
    property order (nested sub-fields first); then, when include_direct is set, this level's own
    direct user extensions (sorted). Returns '' when the subtree contains no extensions."""

    parts = []
    for (name, sub_order) in child_order:
        if not sub_order:
            continue
        for child in [c for c in children if c[0] == name]:
            inner = _field_extensions(child[2], sub_order, cbv_version, True)
            if inner:
                display = "" if (name == "sensorElementList"
                                 and not profile_for(cbv_version).keep_sensor_element_list) else name
                # JOIN_BY is "" for the hash
                parts.append(display + (JOIN_BY if display else "") + inner)
    if include_direct:
        direct = [c for c in children if isinstance(c, tuple) and '{' in c[0] and '/}' in c[0]]
        if direct:
            parts.append(_generic_child_list_to_prehash_string(direct))
    return JOIN_BY.join(parts)



def derive_prehashes_from_events(events, join_by=DEFAULT_JOIN_BY, cbv_version=DEFAULT_CBV_VERSION):
    """
    Compute a normalized form (pre-hash string) for each event.
    This is the main functionality of the hash generator.

    Args:
        events: List of EPCIS events
        join_by: String to join pre-hash components
        cbv_version: CBV version for timestamp processing (CBV2.0 or CBV2.1)
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
            standard = _recurse_through_children_in_order(event[2], PROP_ORDER, cbv_version)
            if profile_for(cbv_version).inline_user_extensions:
                # CBV2.1: field extensions already inline; ilmd + event-level extensions here (sorted)
                trailing = _gather_elements_not_in_order(event[2], PROP_ORDER)
            else:
                # CBV2.0: ilmd, then standard-field extensions (property order, prefixed), then event-level
                ilmd_nodes = [c for c in event[2] if c[0] == 'ilmd']
                for n in ilmd_nodes:
                    event[2].remove(n)
                ilmd_str = _generic_child_list_to_prehash_string(ilmd_nodes) if ilmd_nodes else ""
                # Emit user extensions inside standard fields (prefixed by the field-name path), in property order, and REMOVE each consumed node
                field_ext_parts = []
                for (name, sub_order) in PROP_ORDER:
                    if not sub_order:
                        continue
                    for child in [c for c in event[2] if c[0] == name]:
                        inner = _field_extensions(child[2], sub_order, cbv_version)
                        if inner:
                            display = "" if (name == "sensorElementList"
                                             and not profile_for(cbv_version).keep_sensor_element_list) else name
                            field_ext_parts.append(display + (JOIN_BY if display else "") + inner)
                            event[2].remove(child)
                field_ext = JOIN_BY.join(field_ext_parts)
                event_ext = _gather_elements_not_in_order(event[2], PROP_ORDER)
                trailing = JOIN_BY.join([s for s in (ilmd_str, field_ext, event_ext) if s])
            prehash_string_list.append("eventType=" + event[0] + JOIN_BY + standard + JOIN_BY + trailing)
        except Exception as ex:
            logging.error("could not parse event:\n%s\n\nerror: %s", event, ex)
            logging.debug("".join(traceback.format_tb(ex.__traceback__)))
            pass

    # To see/check concatenated value string before hash algorithm is performed:
    logging.debug("prehash_string_list = {}".format(prehash_string_list))
    return prehash_string_list


def calculate_hashes_from_pre_hashes(prehash_string_list, hashalg="sha256", cbv_version=DEFAULT_CBV_VERSION):
    """Hash all strings in the list with the given algorithm. Returned in the appropriate NI format.

    Args:
        prehash_string_list: List of pre-hash strings to hash
        hashalg: Hash algorithm to use (sha256, sha3-256, sha384, sha512)
        cbv_version: CBV version to include in the hash URL (CBV2.0 or CBV2.1)
    """
    hashValueList = []

    # get "?ver=CBV2.0" / "?ver=CBV2.1" from the single registry
    suffix = profile_for(cbv_version).uri_suffix

    for pre_hash_string in prehash_string_list:
        if hashalg == 'sha256':
            hash_string = 'ni:///sha-256;' + \
                          hashlib.sha256(pre_hash_string.encode('utf-8')).hexdigest() + suffix
        elif hashalg == 'sha3-256':
            hash_string = 'ni:///sha3-256;' + \
                          hashlib.sha3_256(pre_hash_string.encode('utf-8')).hexdigest() + suffix
        elif hashalg == 'sha384':
            hash_string = 'ni:///sha-384;' + \
                          hashlib.sha384(pre_hash_string.encode('utf-8')).hexdigest() + suffix
        elif hashalg == 'sha512':
            hash_string = 'ni:///sha-512;' + \
                          hashlib.sha512(pre_hash_string.encode('utf-8')).hexdigest() + suffix
        else:
            raise ValueError("Unsupported Hashing Algorithm: " + hashalg)

        hashValueList.append(hash_string)

    return hashValueList


def epcis_hashes_from_events(events, hashalg="sha256", cbv_version=DEFAULT_CBV_VERSION):
    """Calculate the list of hashes from the given events list
    + hashing algorithm through the pre hash string using default parameters.

    Args:
        events: List of EPCIS events
        hashalg: Hash algorithm to use (sha256, sha3-256, sha384, sha512)
        cbv_version: CBV version to include in the hash URL (CBV2.0 or CBV2.1)
    """
    prehash_string_list = derive_prehashes_from_events(events, cbv_version=cbv_version)
    return calculate_hashes_from_pre_hashes(prehash_string_list, hashalg, cbv_version)
