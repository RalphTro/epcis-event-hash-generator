# epcis-event-hash-generator
(PROTOTYPE) Provides the means to uniquely identify/validate the integrity of any EPCIS event through a common, syntax-agnostic approach based on hashing. Takes an EPCIS event (formatted in either XML or JSON-LD) and returns a hash value.

## Introduction  


## Functionality/procedure 
For any given EPCIS event, extract and concatenate the values of the following attributes according to the following sequence. Note that all values MUST be added in the identical order as specified below. Data MUST NOT be added if any field is omitted in a given event or does not apply.  

* eventType
  eventTime
eventTimeZoneOffset
ErrorDeclaration – declarationTime
ErrorDeclaration – reason
ErrorDeclaration – correctiveEventIDs (i.e. each individual event ID in exactly the same sequence as it appears in the correctiveEventIDs element)
epcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the epcList)
parentID  
inputEpcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the inputEpcList)
outputEpcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the outputEpcList)
quantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the quantityList)
inputQuantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the inputQuantityList)
outputQuantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the outputQuantityList)
action
bizStep
disposition
readPoint
bizLocation
bizTransactionList – bizTransaction (i.e. each individual bizTransaction ID in exactly the same sequence as it appears in the bizTransactionList)
sourceList – source (i.e. each individual source ID in exactly the same sequence as it appears in the sourceList)
destinationList – destination (i.e. each individual destination ID in exactly the same sequence as it appears in the destinationList)
sensorElement – sensorMetaData – time
sensorElement – sensorMetaData – startTime
sensorElement – sensorMetaData – endTime
sensorElement – sensorMetaData – deviceID
sensorElement – sensorMetaData – deviceMetaData
sensorElement – sensorMetaData – rawData
sensorElement – sensorMetaData – dataProcessingMethod
sensorElement – sensorMetaData – bizRules
sensorElement – sensorReport – type
sensorElement – sensorReport – deviceID
sensorElement – sensorReport – deviceMetaData
sensorElement – sensorReport – rawData
sensorElement – sensorReport – dataProcessingMethod
sensorElement – sensorReport – time
sensorElement – sensorReport – microorganism
sensorElement – sensorReport – chemicalSubstance
sensorElement – sensorReport –  value
sensorElement – sensorReport – valueType
sensorElement – sensorReport – minValue
sensorElement – sensorReport – maxValue
sensorElement – sensorReport – averageValue
sensorElement – sensorReport – sDev
sensorElement – sensorReport – percRank
sensorElement – sensorReport – percValue
sensorElement – sensorReport – uom

## Installation
tbd

## Usage/Short test script 
tbd

## References
* EPCIS Standard, v. 1.2: https://www.gs1.org/standards/epcis
* Core Business Vocabulary (CBV) Standard, v. 1.2.2: https://www.gs1.org/standards/epcis
