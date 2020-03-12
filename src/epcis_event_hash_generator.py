#!/usr/bin/python3
"""This is a prove of concept implementation of an algorithm to calculate a hash of EPCIS events. A small command line utility to calculate the hashes is provided for convenience.

.. module:: epcis_event_hash_generator
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

import logging
import sys
import re
import hashlib
import os

# import syntax differs depending on whether this is run as a module or as a script
try:
    from .xml_to_py import event_list_from_epcis_document_xml as read_xml
    from .json_to_py import event_list_from_epcis_document_json as read_json
    from . import PROP_ORDER
except ImportError:
    from xml_to_py import event_list_from_epcis_document_xml as read_xml
    from json_to_py import event_list_from_epcis_document_json as read_json
    from __init__ import PROP_ORDER
    

def recurse_through_children_in_order(root, child_order):
    """Fetch all texts from root (if it is a simple element) or its
    children and concatenate the values in the given order. child_order is
    expected to be a property order, see PROP_ORDER.

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
                logging.debug("Adding text '%s'", child[1])
                list_of_values.append(child_name + "=" + child[1].strip()) #stripping white space unfortunately not always automatic

        #sort list of values to resolve issue 10
        logging.debug("sorting values %s", list_of_values)
        list_of_values.sort()
        logging.debug("sorted: %s", list_of_values)
        texts += prefix + "".join(list_of_values)

    return texts

def generic_element_to_prehash_string(root):
    list_of_values = []

    logging.debug("Parsing remaining elements: %s", root)
    if isinstance(root, str) and root:
        list_of_values.append("=" + root.strip())
    else:
        for child in root:      
            list_of_values.append( child[0].replace("{","").replace("}","#") + generic_element_to_prehash_string(child[1])+ generic_element_to_prehash_string(child[2]))

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

def compute_prehash_from_file(path, enforce = None):
    """Read EPCIS document and generate pre-hashe strings.
    Use enforce = "XML" or "JSON" to ignore file ending.
    """
    if enforce == "XML" or path.lower().endswith(".xml"):
        events = read_xml(path)
    elif enforce == "JSON" or path.lower().endswith(".json"):
        events = read_json(path)
    else:
        logging.error("Filename '%s' ending not recognized.", path)
    
    logging.debug("#events = %s\neventList = %s", len(events[2]), events)
    
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
                hashlib.sha256(pre_hash_string.encode('utf-8')).hexdigest()
        elif hashalg == 'sha3_256':
            hash_string = 'ni:///sha3_256;' + \
                hashlib.sha3_256(pre_hash_string.encode('utf-8')).hexdigest()
        elif hashalg == 'sha384':
            hash_string = 'ni:///sha-384;' + \
                hashlib.sha384(pre_hash_string.encode('utf-8')).hexdigest()
        elif hashalg == 'sha512':
            hash_string = 'ni:///sha-512;' + \
                hashlib.sha512(pre_hash_string.encode('utf-8')).hexdigest()
        else:
            raise ValueError("Unsupported Hashing Algorithm: " + hash_string)
        
        hashValueList.append(hash_string)

    return (hashValueList, prehash_string_list)


def command_line_parsing():
    import argparse

    logger_cfg = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser = argparse.ArgumentParser(
        description="Generate a canonical hash from an EPCIS Document.")
    parser.add_argument("file", help="EPCIS file", nargs="+")
    parser.add_argument(
        "-a",
        "--algorithm",
        help="Hashing algorithm to use.",
        choices=["sha256", "sha3_256", "sha384", "sha512"],
        default="sha256")
    parser.add_argument(
        "-l",
        "--log",
        help="Set the log level. Default: INFO.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO")
    parser.add_argument(
        "-b",
        "--batch",
        help="If given, write the new line separated list of hashes for each input file into a sibling output file with the same name + '.hashes' instead of stdout.",
        action="store_true")
    parser.add_argument(
        "-p",
        "--prehash",
        help="If given, also output the prehash string to stdout. Output to a .prehashes file, if combined with -b.",
        action="store_true")
    

    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    #print("Log messages above level: {}".format(logger_cfg["level"]))

    if not args.file:
        logging.critical("File name required.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.debug("reading from files: '{}'".format(args.file))

    return args


def main():
    """The main function reads the path to the xml file
    and optionally the hash algorithm from the command
    line arguments and calls the actual algorithm.
    """

    args = command_line_parsing()
            
    for filename in args.file:
        
        # ACTUAL ALGORITHM CALL:
        (hashes, prehashes) = epcis_hash(filename, args.algorithm)

        # Output:
        if args.batch:
            with open(os.path.splitext(filename)[0] + '.hashes', 'w') as outfile:
                outfile.write("\n".join(hashes) + "\n")
            if args.prehash:
                with open(os.path.splitext(filename)[0] + '.prehashes', 'w') as outfile:
                    outfile.write("\n".join(prehashes)+"\n")
        else:
            print("\n\nHashes of the events contained in '{}':\n".format(filename) + "\n".join(hashes))
            if args.prehash:
                print("\nPre-hash strings:\n" +"\n---\n".join(prehashes))


# goto main if script is run as entrypoint
if __name__ == "__main__":
    main()
