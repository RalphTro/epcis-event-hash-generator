import xml.etree.ElementTree as ET
from collections import Counter
import re
import hashlib

def xmlEpcisHash(path, hashalg):

    with open(path, 'rb') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    xml = root

    # Pass entire xml document as a string:
    xml_str = ET.tostring(xml).decode()
    docElements = []
    docElements.extend(elem.tag for elem in root.iter())
    c = Counter(docElements)

    # Variables storing number of EPCIS events per type + total:
    oEvCount = c['ObjectEvent']
    aEvCount = c['AggregationEvent']
    tEvCount = c['TransactionEvent']
    xEvCount = c['TransformationEvent']
    pEvCount = c['AssociationEvent']
    totalCount = oEvCount + aEvCount + tEvCount + xEvCount + pEvCount

    # Extract all events that are part of eventList
    eventListString = xml_str[(re.search('<EventList>', xml_str).start(
    ) + 11): (re.search('</EventList>', xml_str).end() - 12)]

    # Remove all <extension> and <baseExtension> tags, new lines, tabs
    cleanedUpELS = eventListString.replace('<extension>', '').replace('</extension>', '').replace(
        '<baseExtension>', '').replace('</baseExtension>', '').replace('\t', '').replace('\n', '')

    # Add extracted events to eventList/remove them from cleanedUpELS
    eventList = []
    for e in range(oEvCount):
        try:
            eventSegment = (cleanedUpELS[re.search('<ObjectEvent>', cleanedUpELS).start(
            ): re.search('</ObjectEvent>', cleanedUpELS).end()])
            eventList.append(eventSegment)
            cleanedUpELS = cleanedUpELS.replace(eventSegment, '')
        except AttributeError:
            pass
    for e in range(aEvCount):
        try:
            eventSegment = (cleanedUpELS[re.search('<AggregationEvent>', cleanedUpELS).start(
            ): re.search('</AggregationEvent>', cleanedUpELS).end()])
            eventList.append(eventSegment)
            cleanedUpELS = cleanedUpELS.replace(eventSegment, '')
        except AttributeError:
            pass
    for e in range(tEvCount):
        try:
            eventSegment = (cleanedUpELS[re.search('<TransactionEvent>', cleanedUpELS).start(
            ): re.search('</TransactionEvent>', cleanedUpELS).end()])
            eventList.append(eventSegment)
            cleanedUpELS = cleanedUpELS.replace(eventSegment, '')
        except AttributeError:
            pass
    for e in range(xEvCount):
        try:
            eventSegment = (cleanedUpELS[re.search('<TransformationEvent>', cleanedUpELS).start(
            ): re.search('</TransformationEvent>', cleanedUpELS).end()])
            eventList.append(eventSegment)
            cleanedUpELS = cleanedUpELS.replace(eventSegment, '')
        except AttributeError:
            pass
    for e in range(pEvCount):
        try:
            eventSegment = (cleanedUpELS[re.search('<AssociationEvent>', cleanedUpELS).start(
            ): re.search('</AssociationEvent>', cleanedUpELS).end()])
            eventList.append(eventSegment)
            cleanedUpELS = cleanedUpELS.replace(eventSegment, '')
        except AttributeError:
            pass

    # Fetch all standard attribute values of the contained events, concatenate them and write the result into prehashStringList
    prehashStringList = []
    t = 0
    while t < totalCount:
        def fetchRepeatableValues(position, fieldname):
            try:
                a = 0
                valueString = str()
                while a < (d[fieldname]):
                    valueString = valueString + root2.find(position)[a].text
                    a = a + 1
                return (valueString)
            except (AttributeError, IndexError):
                pass

        def fetchQuantityValues(epcClassPos, quantityPos, uomPos, fieldname):
            try:
                q = 0
                quantityList = str()
                while q < (d[fieldname]):
                    try:
                        quantityList = quantityList + \
                            root2.findall(epcClassPos)[q].text
                    except IndexError:
                        pass
                    try:
                        quantityList = quantityList + \
                            root2.findall(quantityPos)[q].text
                    except IndexError:
                        pass
                    try:
                        quantityList = quantityList + \
                            root2.findall(uomPos)[q].text
                    except IndexError:
                        pass
                    q = q + 1
                return (quantityList)
            except AttributeError:
                pass
        try:
            tree2 = ET.ElementTree(ET.fromstring(eventList[t]))
            root2 = tree2.getroot()
            docElements2 = []
            docElements2.extend(elem.tag for elem in root2.iter())
            d = Counter(docElements2)
        except (IndexError, ET.ParseError):
            pass
        try:
            preHashString = root2.find('eventTime').text
        except (AttributeError):
            pass
        try:
            preHashString = preHashString + \
                root2.find('eventTimeZoneOffset').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('eventID').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + \
                root2.find('errorDeclaration/declarationTime').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + \
                root2.find('errorDeclaration/reason').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues(
                    'errorDeclaration/correctiveEventIDs', 'correctiveEventID')
        except TypeError:
            pass
        try:
            if str(eventList[t]).startswith('<TransactionEvent>') == True:
                preHashString = preHashString + \
                    fetchRepeatableValues(
                        'bizTransactionList', 'bizTransaction')
        except IndexError:
            pass
        try:
            preHashString = preHashString + root2.find('parentID').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues('epcList', 'epc')
        except TypeError:
            pass
        try:
            i = 0
            inputEpcCount = len(root2.findall('inputEPCList/epc'))
            while i < inputEpcCount:
                try:
                    preHashString = preHashString + \
                        root2.findall('inputEPCList/epc')[i].text
                    i = i + 1
                except IndexError:
                    pass
        except TypeError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues('childEPCs', 'epc')
        except TypeError:
            pass
        try:
            preHashString = preHashString + fetchQuantityValues('quantityList/quantityElement/epcClass',
                                                                'quantityList/quantityElement/quantity', 'quantityList/quantityElement/uom', 'quantityElement')
        except TypeError:
            pass
        try:
            preHashString = preHashString + fetchQuantityValues('childQuantityList/quantityElement/epcClass',
                                                                'childQuantityList/quantityElement/quantity', 'childQuantityList/quantityElement/uom', 'quantityElement')
        except TypeError:
            pass
        try:
            preHashString = preHashString + fetchQuantityValues('inputQuantityList/quantityElement/epcClass',
                                                                'inputQuantityList/quantityElement/quantity', 'inputQuantityList/quantityElement/uom', 'quantityElement')
        except TypeError:
            pass
        try:
            o = 0
            inputEpcCount = len(root2.findall('outputEPCList/epc'))
            while o < inputEpcCount:
                try:
                    preHashString = preHashString + \
                        root2.findall('outputEPCList/epc')[o].text
                    o = o + 1
                except IndexError:
                    pass
        except TypeError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues('outputEPCList', 'epc')
        except TypeError:
            pass
        try:
            preHashString = preHashString + fetchQuantityValues('outputQuantityList/quantityElement/epcClass',
                                                                'outputQuantityList/quantityElement/quantity', 'outputQuantityList/quantityElement/uom', 'quantityElement')
        except TypeError:
            pass
        try:
            preHashString = preHashString + root2.find('action').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('transformationID').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('bizStep').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('disposition').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('readPoint/id').text
        except AttributeError:
            pass
        try:
            preHashString = preHashString + root2.find('bizLocation/id').text
        except AttributeError:
            pass
        try:
            if str(eventList[t]).startswith('<ObjectEvent>') or str(eventList[t]).startswith('<AggregationEvent>') or str(eventList[t]).startswith('<TransformationEvent>') or str(eventList[t]).startswith('<AssociationEvent>') == True:
                preHashString = preHashString + \
                    fetchRepeatableValues(
                        'bizTransactionList', 'bizTransaction')
        except IndexError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues('sourceList', 'source')
        except TypeError:
            pass
        try:
            preHashString = preHashString + \
                fetchRepeatableValues('destinationList', 'destination')
        except TypeError:
            pass
        for elem in root2.iterfind('sensorElementList/sensorElement/sensorMetaData'):
            sensorMetaDataDict = (elem.tag, elem.attrib)[1]
            if 'time' in sensorMetaDataDict:
                preHashString = preHashString + sensorMetaDataDict.get('time')
            if 'startTime' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('startTime')
            if 'endTime' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('endTime')
            if 'deviceID' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('deviceID')
            if 'deviceMetaData' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('deviceMetaData')
            if 'rawData' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('rawData')
            if 'dataProcessingMethod' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('dataProcessingMethod')
            if 'bizRules' in sensorMetaDataDict:
                preHashString = preHashString + \
                    sensorMetaDataDict.get('bizRules')
            for elem in root2.iterfind('sensorElementList/sensorElement/sensorReport'):
                sensorReportDict = (elem.tag, elem.attrib)[1]
                if 'type' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('type')
                if 'deviceID' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('deviceID')
                if 'deviceMetaData' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('deviceMetaData')
                if 'rawData' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('rawData')
                if 'dataProcessingMethod' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('dataProcessingMethod')
                if 'time' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('time')
                if 'microorganism' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('microorganism')
                if 'chemicalSubstance' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('chemicalSubstance')
                if 'value' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('value')
                if 'stringValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('stringValue')
                if 'booleanValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('booleanValue')
                if 'hexBinaryValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('hexBinaryValue')
                if 'uriValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('uriValue')
                if 'minValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('minValue')
                if 'maxValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('maxValue')
                if 'meanValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('meanValue')
                if 'sDev' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('sDev')
                if 'percRank' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('percRank')
                if 'percValue' in sensorReportDict:
                    preHashString = preHashString + \
                        sensorReportDict.get('percValue')
                if 'uom' in sensorReportDict:
                    preHashString = preHashString + sensorReportDict.get('uom')
        prehashStringList.append(preHashString)

        # Calculate hash values and prefix them according to RFC 6920
        hashValueList = []
        for h in range(len(prehashStringList)):
            if hashalg == 'sha256':
                hashString = 'ni:///sha-256;' + \
                    hashlib.sha256(preHashString.encode('utf-8')).hexdigest()
            elif hashalg == 'sha3_256':
                hashString = 'ni:///sha3_256;' + \
                    hashlib.sha3_256(preHashString.encode('utf-8')).hexdigest()
            elif hashalg == 'sha384':
                hashString = 'ni:///sha-384;' + \
                    hashlib.sha384(preHashString.encode('utf-8')).hexdigest()
            elif hashalg == 'sha512':
                hashString = 'ni:///sha-512;' + \
                    hashlib.sha512(preHashString.encode('utf-8')).hexdigest()
            hashValueList.append(hashString)
        t = t + 1

    # To see/check concatenated value string before hash algorithm is performed:
    print(prehashStringList)
    return (hashValueList)


def main():
    """The main function reads the path to the xml file
    and optionally the hash algorithm from the command
    line arguments and calls the actual algorithm.
    """
    import argparse

    logger_cfg = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser = argparse.ArgumentParser(
        description="Generate a canonical hash from an EPCIS Document.")
    parser.add_argument("-f", "--file", help="EPCIS file")
    parser.add_argument(
        "-a",
        "--algorithm",
        help="Hashing algorithm to use.",
        choices=["sha256", "sha3_256", "sha384", "sha512"],
        default="sha256")
    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    print("Log messages above level: {}".format(logger_cfg["level"]))

    if not args.file:
        logging.critical("No gile given.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.info("reading from file: '{}'".format(args.file))

    print(xmlEpcisHash(args.file, args.algorithm))


# goto main if script is run as entrypoint
if __name__ == "__main__":
    main()
