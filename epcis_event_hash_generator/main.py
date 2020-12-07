#!/usr/bin/python3
""" This is a small command line utility to calculate the hashes using the epcis_event_hash_generator algorithm.

.. module:: main
   :synopsis: Command line utility to calculate the EPCIS event hash as specified in
              https://github.com/RalphTro/epcis-event-hash-generator/

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>, Sebastian Schmittner <schmittner@eecc.info>

Copyright 2019-2020 Ralph Troeger, Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

# import syntax differs depending on whether this is run as a module or as a script
try:
    from .context import epcis_event_hash_generator
except ImportError:
    from context import epcis_event_hash_generator  # noqa: F401

import argparse
import logging
import os
import sys

from epcis_event_hash_generator import hash_generator


def command_line_parsing():
    logger_cfg = {
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
        default="WARNING")
    parser.add_argument(
        "-b",
        "--batch",
        help="If given, write the new line separated list of hashes for each input file into a sibling output file "
             "with the same name + '.hashes' instead of stdout.",
        action="store_true")
    parser.add_argument(
        "-p",
        "--prehash",
        help="If given, also output the prehash string to stdout. Output to a .prehashes file, if combined with -b.",
        action="store_true")
    parser.add_argument(
        "-j",
        "--join",
        help="String used to join the pre hash string." +
        " Defaults to empty string as specified. Values like '\\n' might be useful for debugging.",
        default="")

    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    # print("Log messages above level: {}".format(logger_cfg["level"]))

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

    logging.debug("Running cli tool with arguments %s", args)

    for filename in args.file:
        # ACTUAL ALGORITHM CALL:
        (hashes, prehashes) = hash_generator.epcis_hash(filename, args.algorithm, args.join)

        # Output:
        if args.batch:
            with open(os.path.splitext(filename)[0] + '.hashes', 'w') as outfile:
                outfile.write("\n".join(hashes) + "\n")
            if args.prehash:
                with open(os.path.splitext(filename)[0] + '.prehashes', 'w') as outfile:
                    outfile.write("\n".join(prehashes) + "\n")
        else:
            print("\n\nHashes of the events contained in '{}':\n".format(filename) + "\n".join(hashes))
            if args.prehash:
                print("\nPre-hash strings:\n" + "\n---\n".join(prehashes))


# goto main if script is run as entrypoint
if __name__ == "__main__":
    main()
