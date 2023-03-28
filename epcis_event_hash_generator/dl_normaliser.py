"""
GS1 Digital Link Normaliser.

This script accepts any valid URI scheme accommodating a GS1 ID,
i.e. EPC URIs, EPC Class URIs, EPC ID Pattern URIs, or GS1 Digital Link URIs.
It converts all of them into one normalised form, meaning that it
(a) converts it into a canonical GS1 DL URI,
(b) ensures that it only contains the most fine-granular ID level,
(c) strips off any further attributes.

.. module:: dl_normaliser
   :synopsis: Normalises the gs1 id formats to digital link for https://github.com/RalphTro/epcis-event-hash-generator/

.. moduleauthor:: Ralph Troeger <ralph.troeger@gs1.de>

Copyright 2019-2023 Ralph Troeger

This program is free software: you can redistribute it and/or modify
it under the terms given in the LICENSE file.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the LICENSE
file for details.

"""

from re import match
import logging
import math


def __web_uri_percent_encoder(input):
    """Function percent-encodes URL-unsafe characters in GS1 Digital Link URIs.

    Table 7-1 in the GS1 Digital Link Standard requires
    the following symbols to be percent-encoded:
    '!', space, '#', '%', '&', '(', ')', '*', '+', ',', '/', ':'
    EPC URIs already prohibit some of them (e.g. '#')
    Function 'webURIPercentEncoder' is called to ensure that
    data elements accommodating these symbols are percent-encoded.

    Parameters
    ----------
    input : str
        Character requiring percent-encoding.

    Returns
    -------
    str
        Percent-encoded equivalent of character.
    """

    return (input.replace('!', '%21')
            .replace('(', '%28')
            .replace(')', '%29')
            .replace('*', '%2A')
            .replace('+', '%2B')
            .replace(',', '%2C')
            .replace(':', '%3A'))


def check_digit(key_wo_checkdigit):
    """Returns check digit for GTIN-8, GTIN-12, GTIN-13, GLN, GTIN-14, SSCC, GSIN, GSRN, GSRN-P.
    For further details, see GS1 GenSpecs, section 7.9.1: Standard check digit calculations for GS1 data structures.

    Parameters
    ----------
    key_wo_checkdigit : str
        GS1 key without check digit.

    Returns
    -------
        str: Check digit for GS1 key.
    """

    # Reverse string
    key_wo_checkdigit = key_wo_checkdigit[::-1]
    # Alternatively fetch digits, multiply them by 3 or 1, and sum them up
    summation = 0
    for i in range(len(key_wo_checkdigit) - 1, -1, -1):
        if int(key_wo_checkdigit[i]) == 0:
            continue
        elif i % 2 != 0:
            summation += int(key_wo_checkdigit[i]) * 1
        else:
            summation += int(key_wo_checkdigit[i]) * 3
    # Subtract sum from nearest equal or higher multiple of ten
    checkdigit = math.ceil(summation / 10) * 10 - summation
    return checkdigit


def normaliser(uri):
    """Function converts any standard URI conveying a GS1 Key in Canonical GS1 DL URI.

    Function 'normaliser' expects any URI to be used in EPCIS events
    that convey a GS1 key, i.e. EPC URIs, EPC Class URIs,
    EPC ID Pattern URIs, or GS1 Digital Link URIs.
    It returns a corresponding, constrained version of a
    canonical GS1 Digital Link URI, i.e. with
    the lowest level of identification and without CPV/query string.

    Parameters
    ----------
    uri : str
        Valid EPC URI, EPC Pattern URI, EPC Class URI, GS1 Digital Link URI.

    Returns
    -------
    str
        Constrained, canonicalised GS1 Digital Link URI equivalent.
    None
    """

    if not isinstance(uri, str):
        logging.warning("dl normaliser called with non-string argument")
        return None

    try:
        partition = uri.index('.')
    except ValueError:
        logging.debug("No '.' in %s. Not a normalisable uri.", uri)
        return None

    # EPC URIs
    if match(
            r'^urn:epc:id:sgtin:((\d{6}\.\d{7})|(\d{7}\.\d{6})|(\d{8}\.\d{5})|(\d{9}\.\d{4})|(\d{10}\.\d{3})|(\d{11}\.\d{2})|(\d{12}\.\d{1}))\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}$',
            uri) is not None:
        gs1companyprefix = uri[17:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        serial = uri[32:]
        return ('https://id.gs1.org/01/' + raw_gtin + str(check_digit(raw_gtin)) + '/21/' + __web_uri_percent_encoder(
            serial))

    if match(
            r'^urn:epc:id:sscc:((\d{6}\.\d{11}$)|(\d{7}\.\d{10}$)|(\d{8}\.\d{9}$)|(\d{9}\.\d{8}$)|(\d{10}\.\d{7}$)|(\d{11}\.\d{6}$)|(\d{12}\.\d{5}$))',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        serialref = uri[(partition + 2):]
        rawSSCC = uri[(partition + 1):(partition + 2)] + gs1companyprefix + serialref
        return ('https://id.gs1.org/00/' + rawSSCC + str(check_digit(rawSSCC)))

    if match(
            r'^urn:epc:id:sgln:((\d{6}\.\d{6})|(\d{7}\.\d{5})|(\d{8}\.\d{4})|(\d{9}\.\d{3})|(\d{10}\.\d{2})|(\d{11}\.\d{1})|(\d{12}\.))\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        locationref = uri[(partition + 1):(partition + 1 +
                                           (12 - len(gs1companyprefix)))]
        rawGLN = gs1companyprefix + locationref
        extension = uri[30:]
        if extension == '0':
            return ('https://id.gs1.org/414/' + rawGLN + str(check_digit(rawGLN)))
        else:
            return ('https://id.gs1.org/414/' + rawGLN + str(check_digit(rawGLN)) + '/254/' + __web_uri_percent_encoder(
                extension))

    if match(
            r'^urn:epc:id:grai:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.\.))\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,16}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        assetref = uri[(partition + 1):(partition + 1 + (12 - len(gs1companyprefix)))]
        raw_grai = '0' + gs1companyprefix + assetref
        serial = uri[30:]
        return ('https://id.gs1.org/8003/' + raw_grai + str(check_digit(raw_grai)) + __web_uri_percent_encoder(serial))

    if match(
            r'^urn:epc:id:giai:(([\d]{6}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,24})|([\d]{7}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,23})|([\d]{8}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,22})|([\d]{9}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,21})|([\d]{10}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20})|([\d]{11}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,19})|([\d]{12}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,18}))$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        assetref = uri[(partition + 1):]
        return ('https://id.gs1.org/8004/' + gs1companyprefix + __web_uri_percent_encoder(assetref))

    if match(
            r'^urn:epc:id:gsrn:(([\d]{6}\.[\d]{11}$)|([\d]{7}\.[\d]{10}$)|([\d]{8}\.[\d]{9}$)|([\d]{9}\.[\d]{8}$)|([\d]{10}\.[\d]{7}$)|([\d]{11}\.[\d]{6}$)|([\d]{12}\.[\d]{5}$))',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        serviceref = uri[(partition + 1):]
        rawGSRN = gs1companyprefix + serviceref
        return ('https://id.gs1.org/8018/' + rawGSRN + str(check_digit(rawGSRN)))

    if match(
            r'^urn:epc:id:gsrnp:(([\d]{6}\.[\d]{11}$)|([\d]{7}\.[\d]{10}$)|([\d]{8}\.[\d]{9}$)|([\d]{9}\.[\d]{8}$)|([\d]{10}\.[\d]{7}$)|([\d]{11}\.[\d]{6}$)|([\d]{12}\.[\d]{5}$))',
            uri) is not None:
        gs1companyprefix = uri[17:partition]
        serviceref = uri[(partition + 1):]
        rawGSRNP = gs1companyprefix + serviceref
        return ('https://id.gs1.org/8017/' + rawGSRNP + str(check_digit(rawGSRNP)))

    if match(
            r'^urn:epc:id:gdti:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.\.))(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        documenttype = uri[(partition + 1):(partition + 1 +
                                            (12 - len(gs1companyprefix)))]
        raw_gdti = gs1companyprefix + documenttype
        serial = uri[30:]
        return 'https://id.gs1.org/253/' + raw_gdti + str(check_digit(raw_gdti)) + __web_uri_percent_encoder(serial)

    if match(
            r'^urn:epc:id:cpi:((\d{6}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,24})|(\d{7}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,23})|(\d{8}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,22})|(\d{9}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,21})|(\d{10}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,20})|(\d{11}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,19})|(\d{12}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,18}))\.[\d]{1,12}$',
            uri) is not None:
        gs1companyprefix = uri[15:partition]
        separator = uri.rfind('.')
        cpref = uri[(partition + 1):separator]
        raw_cpi = gs1companyprefix + cpref
        serial = uri[(separator + 1):]
        return 'https://id.gs1.org/8010/' + __web_uri_percent_encoder(raw_cpi) + '/8011/' + serial

    if match(
            r'^urn:epc:id:sgcn:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.))\.[\d]{1,12}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        couponref = uri[(partition + 1):(partition + 1 + (12 - len(gs1companyprefix)))]
        raw_sgcn = gs1companyprefix + couponref
        serial = uri[30:]
        return 'https://id.gs1.org/255/' + raw_sgcn + str(check_digit(raw_sgcn)) + serial

    if match(
            r'^urn:epc:id:ginc:([\d]{6}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,24}|[\d]{7}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,23}|[\d]{8}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,22}|[\d]{9}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,21}|[\d]{10}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}|[\d]{11}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,19}|[\d]{12}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,18})$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        consignmentref = uri[(partition + 1):]
        return 'https://id.gs1.org/401/' + gs1companyprefix + __web_uri_percent_encoder(consignmentref)

    if match(
            r'^urn:epc:id:gsin:(([\d]{6}\.[\d]{10}$)|([\d]{7}\.[\d]{9}$)|([\d]{8}\.[\d]{8}$)|([\d]{9}\.[\d]{7}$)|([\d]{10}\.[\d]{6}$)|([\d]{11}\.[\d]{5}$)|([\d]{12}\.[\d]{4}$))',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        shipperref = uri[(partition + 1):]
        rawGSIN = gs1companyprefix + shipperref
        return 'https://id.gs1.org/402/' + rawGSIN + str(check_digit(rawGSIN))

    if match(
            r'^urn:epc:id:itip:(([\d]{6}\.[\d]{7})|([\d]{7}\.[\d]{6})|([\d]{8}\.[\d]{5})|([\d]{9}\.[\d]{4})|([\d]{10}\.[\d]{3})|([\d]{11}\.[\d]{2})|([\d]{12}\.[\d]{1}))\.[\d]{2}\.[\d]{2}\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        piece = uri[31:33]
        total = uri[34:36]
        serial = uri[37:]
        return 'https://id.gs1.org/8006/' + raw_gtin + str(check_digit(raw_gtin)) + piece + total + \
               '/21/' + __web_uri_percent_encoder(serial)

    if match(
            r'^urn:epc:id:upui:((\d{6}\.\d{7})|(\d{7}\.\d{6})|(\d{8}\.\d{5})|(\d{9}\.\d{4})|(\d{10}\.\d{3})|(\d{11}\.\d{2})|(\d{12}\.\d{1}))\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,28}$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        serial = uri[31:]
        return 'https://id.gs1.org/01/' + raw_gtin + str(check_digit(raw_gtin)) + '/235/' + __web_uri_percent_encoder(serial)

    if match(
            r'^urn:epc:id:pgln:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.))$',
            uri) is not None:
        gs1companyprefix = uri[16:partition]
        partyref = uri[(partition + 1):(partition + 1 + (12 - len(gs1companyprefix)))]
        rawGLN = gs1companyprefix + partyref
        return 'https://id.gs1.org/417/' + rawGLN + str(check_digit(rawGLN))

    # EPC Class URIs
    if match(
            r'^urn:epc:class:lgtin:(([\d]{6}\.[\d]{7})|([\d]{7}\.[\d]{6})|([\d]{8}\.[\d]{5})|([\d]{9}\.[\d]{4})|([\d]{10}\.[\d]{3})|([\d]{11}\.[\d]{2})|([\d]{12}\.[\d]{1}))\.(\%2[125-9A-Fa-f]|\%3[0-9A-Fa-f]|\%4[1-9A-Fa-f]|\%5[0-9AaFf]|\%6[1-9A-Fa-f]|\%7[0-9Aa]|[!\')(*+,.0-9:;=A-Za-z_-]){1,20}$',
            uri) is not None:
        gs1companyprefix = uri[20:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        lot = uri[35:]
        return 'https://id.gs1.org/01/' + raw_gtin + str(check_digit(raw_gtin)) + '/10/' + __web_uri_percent_encoder(lot)

    # EPC ID Pattern URIs
    if match(
            r'^urn:epc:idpat:sgtin:((\d{6}\.\d{7})|(\d{7}\.\d{6})|(\d{8}\.\d{5})|(\d{9}\.\d{4})|(\d{10}\.\d{3})|(\d{11}\.\d{2})|(\d{12}\.\d{1}))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[20:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        return 'https://id.gs1.org/01/' + raw_gtin + str(check_digit(raw_gtin))

    if match(
            r'^urn:epc:idpat:grai:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.\.))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[19:partition]
        assetref = uri[(partition + 1):(partition + 1 + (12 - len(gs1companyprefix)))]
        raw_grai = '0' + gs1companyprefix + assetref
        return 'https://id.gs1.org/8003/' + raw_grai + str(check_digit(raw_grai))

    if match(
            r'^urn:epc:idpat:gdti:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.\.))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[19:partition]
        documenttype = uri[(partition + 1):(partition + 1 +
                                            (12 - len(gs1companyprefix)))]
        raw_gdti = gs1companyprefix + documenttype
        return 'https://id.gs1.org/253/' + raw_gdti + str(check_digit(raw_gdti))

    if match(
            r'^urn:epc:idpat:sgcn:(([\d]{6}\.[\d]{6})|([\d]{7}\.[\d]{5})|([\d]{8}\.[\d]{4})|([\d]{9}\.[\d]{3})|([\d]{10}\.[\d]{2})|([\d]{11}\.[\d]{1})|([\d]{12}\.\.))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[19:partition]
        couponref = uri[(partition + 1):(partition + 1 + (12 - len(gs1companyprefix)))]
        raw_sgcn = gs1companyprefix + couponref
        return 'https://id.gs1.org/255/' + raw_sgcn + str(check_digit(raw_sgcn))

    if match(
            r'^urn:epc:idpat:cpi:((\d{6}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,24})|(\d{7}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,23})|(\d{8}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,22})|(\d{9}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,21})|(\d{10}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,20})|(\d{11}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,19})|(\d{12}\.(\%2[3dfDF]|\%3[0-9]|\%4[1-9A-Fa-f]|\%5[0-9Aa]|[0-9A-Z-]){1,18}))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[18:partition]
        separator = uri.rfind('.')
        cpref = uri[(partition + 1):(separator)]
        raw_cpi = gs1companyprefix + cpref
        return 'https://id.gs1.org/8010/' + __web_uri_percent_encoder(raw_cpi)

    if match(
            r'^urn:epc:idpat:itip:(([\d]{6}\.[\d]{7})|([\d]{7}\.[\d]{6})|([\d]{8}\.[\d]{5})|([\d]{9}\.[\d]{4})|([\d]{10}\.[\d]{3})|([\d]{11}\.[\d]{2})|([\d]{12}\.[\d]{1}))\.[\d]{2}\.[\d]{2}\.\*$',
            uri) is not None:
        gs1companyprefix = uri[19:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        piece = uri[34:36]
        total = uri[37:39]
        return 'https://id.gs1.org/8006/' + raw_gtin + str(check_digit(raw_gtin)) + piece + total

    if match(
            r'^urn:epc:idpat:upui:((\d{6}\.\d{7})|(\d{7}\.\d{6})|(\d{8}\.\d{5})|(\d{9}\.\d{4})|(\d{10}\.\d{3})|(\d{11}\.\d{2})|(\d{12}\.\d{1}))\.\*$',
            uri) is not None:
        gs1companyprefix = uri[19:partition]
        itemref = uri[(partition + 1):(partition + 1 + (13 - len(gs1companyprefix)))]
        raw_gtin = itemref[0:1] + gs1companyprefix + itemref[1:]
        return 'https://id.gs1.org/01/' + raw_gtin + str(check_digit(raw_gtin))

    # GS1 DL URIs
    if match(
            r'^https?:(\/\/((([^\/?#]*)@)?([^\/?#:]*)(:([^\/?#]*))?))?((([^?#]*)(\/(01|gtin|8006|itip|8010|cpid|414|gln|417|party|8017|gsrnp|8018|gsrn|255|gcn|00|sscc|253|gdti|401|ginc|402|gsin|8003|grai|8004|giai)\/)(\d{4}[^\/]+)(\/[^/]+\/[^/]+)?[/]?(\?([^?\n]*))?(#([^\n]*))?)|(\/[A-Za-z_-]{10}$))',
            uri) is None:
        return None

    # remove query string
    if uri.find('?') >= 0:
        uri = uri[:uri.index('?')]

    # replace short names for keys/key extensions with AIs
    uri = (uri.replace('/gtin/', '/01/')
           .replace('/itip/', '/8006/')
           .replace('/cpid/', '/8010/')
           .replace('/gln/', '/414/')
           .replace('/party/', '/417/')
           .replace('/gsrnp/', '/8017/')
           .replace('/gsrn/', '/8018/')
           .replace('/gcn/', '/255/')
           .replace('/sscc/', '/00/')
           .replace('/gdti/', '/253/')
           .replace('/ginc/', '/401/')
           .replace('/gsin/', '/402/')
           .replace('/grai/', '/8003/')
           .replace('/giai/', '/8004/')
           .replace('/cpv/', '/22/')
           .replace('/lot/', '/10/')
           .replace('/ser/', '/21/'))

    # prefix with canonical domain name
    if match(
            r'^https:\/\/id.gs1.org\/(01|8006|8010|414|417|8017|8018|255|00|253|401|402|8003|8004)\/(\d{4}[^\/]+)(\/[^\/]+\/[^\/]+)?[\/]?(\?([^?\n]*))?(#([^\n]*))?|(\/[A-Za-z_-]{10}$)',
            uri) is None:
        if uri.find('/00/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/00/')):]
        elif uri.find('/01/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/01/')):]
        elif uri.find('/253/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/253/')):]
        elif uri.find('/255/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/255/')):]
        elif uri.find('/401/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/401/')):]
        elif uri.find('/402/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/402/')):]
        elif uri.find('/414/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/414/')):]
        elif uri.find('/417/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/417/')):]
        elif uri.find('/8003/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8003/')):]
        elif uri.find('/8004/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8004/')):]
        elif uri.find('/8006/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8006/')):]
        elif uri.find('/8010/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8010/')):]
        elif uri.find('/8017/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8017/')):]
        elif uri.find('/8018/') != -1:
            uri = 'https://id.gs1.org' + uri[(uri.find('/8018/')):]

    # ensure that all GTIN formats are padded to 14 digits
    if match(r'^https:\/\/id.gs1.org\/01\/\d{14}', uri) is None:
        if match(r'^https:\/\/id.gs1.org\/01\/\d{13}', uri) is not None:
            uri = uri.replace('/01/', '/01/0')
        elif match(r'^https:\/\/id.gs1.org\/01\/\d{12}', uri) is not None:
            uri = uri.replace('/01/', '/01/00')
        elif match(r'^https:\/\/id.gs1.org\/01\/\d{8}', uri) is not None:
            uri = uri.replace('/01/', '/01/000000')

    # remove cpv
    x = uri[(uri.find('/22/') + 4):]

    # for 01/8006 only:
    if (
            match(
                r'https:\/\/id.gs1.org\/8006\/\d{18}\/22\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
                uri) or match(
                    r'https:\/\/id.gs1.org\/01\/\d{14}\/22\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
                    uri)) is not None:
        uri = (uri[:(uri.find('/22/'))]) + (x[x.find('/'):-1])

    # for 01/8006 followed by other key qualifiers:
    if (
            match(
                r'https:\/\/id.gs1.org\/8006\/\d{18}\/22\/([\x2F\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
                uri) or match(
                    r'https:\/\/id.gs1.org\/01\/\d{14}\/22\/([\x2F\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
                    uri)) is not None:
        uri = (uri[:(uri.find('/22/'))]) + (x[x.find('/'):])

    # take only lowest ID granularity level (i.e. if serial is present, omit lot)
    if (match(
            r'https:\/\/id.gs1.org\/8006\/\d{18}\/10\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})\/21\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or match(
                r'https:\/\/id.gs1.org\/01\/(\d{14})\/10\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})\/21\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
                uri)) is not None:
        y = uri[(uri.find('/10/') + 4):]
        uri = (uri[:(uri.find('/10/'))]) + (y[y.find('/'):])

    # ensure that output has a valid syntax
    if (match(r'https:\/\/id.gs1.org\/00\/(\d{18})$', uri) or
        match(
            r'https:\/\/id.gs1.org\/01\/(\d{14})\/21\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or
        match(
            r'https:\/\/id.gs1.org\/01\/(\d{14})\/10\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or
        match(r'https:\/\/id.gs1.org\/01\/(\d{14})$', uri) or
        match(
            r'https:\/\/id.gs1.org\/01\/(\d{14})\/235\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,28})$',
            uri) or
        match(r'https:\/\/id.gs1.org\/253\/(\d{13})([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,17})$',
              uri) or
        match(r'https:\/\/id.gs1.org\/255\/(\d{13})(\d{0,12})$', uri) or
        match(r'https:\/\/id.gs1.org\/401\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,30})$', uri) or
        match(r'https:\/\/id.gs1.org\/402\/(\d{17})$', uri) or
        match(r'https:\/\/id.gs1.org\/414\/(\d{13})$', uri) or
        match(
            r'https:\/\/id.gs1.org\/414\/(\d{13})\/254\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or
        match(r'https:\/\/id.gs1.org\/417\/(\d{13})$', uri) or
        match(
            r'https:\/\/id.gs1.org\/8003\/(\d{14})([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,16})$',
            uri) or
        match(r'https:\/\/id.gs1.org\/8004\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,30})$',
              uri) or
        match(
            r'https:\/\/id.gs1.org\/8006\/(\d{18})\/21\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or
        match(
            r'https:\/\/id.gs1.org\/8006\/(\d{18})\/10\/([\x22\x27\x2D\x2E\x30-\x39\x3B-\x3F\x41-\x5A\x5F\x61-\x7A]{0,20})$',
            uri) or
        match(r'https:\/\/id.gs1.org\/8006\/(\d{18})$', uri) or
        match(r'https:\/\/id.gs1.org\/8010\/([\x23\x2D\x2F\x30-\x39\x41-\x5A]{0,30})\/8011/(\d{0,12})$', uri) or
        match(r'https:\/\/id.gs1.org\/8010\/([\x23\x2D\x2F\x30-\x39\x41-\x5A]{0,30})$', uri) or
        match(r'https:\/\/id.gs1.org\/8017\/(\d{18})$', uri) or
        match(r'https:\/\/id.gs1.org\/8018\/(\d{18})$', uri)
    ) is not None:  # noqa E124
        return uri
    return None
