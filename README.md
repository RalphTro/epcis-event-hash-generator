# epcis-event-hash-generator
Provides the means to uniquely identify/validate the integrity of any EPCIS event through a common, syntax-agnostic approach based on hashing. 
This <b>PROTOTYPE</b> takes an EPCIS event (formatted in XML and without any embracing XML super-elements) and returns a hash value representing a unique fingerprint of the latter. In addition, it may be useful to compare the values it returns with those of your own implementation.     

## Introduction  
There are situations in which organisations require to uniquely refer to a specific EPCIS event. For instance, companies may only want to store the <b>hash value of a given EPCIS event on a distributed shared ledger ('blockchain')</b> instead of any actual payload. Digitally signed and in conjunction with a unique timestamp, this is a powerful and effective way to prove the integrity of the underlying event data. Another use case consists to use such an approach to <b>populate the eventID field with values that are intrinsic to the EPCIS event</b>  - if an organisation captures an event without an eventID (which is not required as of the standard) and sends that event to a solution provider who needs to assign a unique ID, they can agree that the solution provider populates the eventID field applying this methodology before storing the event on the server. If the organisation later wants to query for that specific event, it knows how the eventID was created, thus is able to query for it via the eventID.
EPCIS events have a couple of differences to other electronic documents:
+ They are embedded in an EPCIS document that can contain multiple events 
+ As of EPCIS 2.0, it is permitted to capture and share EPCIS data through two different syntaxes (XML and JSON-LD)
+ EPCIS events provides ample flexibility to include user-specific extensions 
+ When expressed in JSON, the sequence of elements may vary

This is why industry needs to have a consistent, reliable approach to create a hash value that is viable to uniquely identify a specific EPCIS event. 

## Functionality/procedure 
For any given EPCIS event, extract and concatenate the values of the following attributes according to the following sequence. Note that all values MUST be added in the identical order as specified below (corresponding to the order in which they are specified in the EPCIS standard). Data MUST NOT be added if any field is omitted in a given event or does not apply.  

Seq. | ObjectEvent | AggregationEvent | TransactionEvent | TransformationEvent | AssociationEvent
--- | --- | --- | --- |--- |--- 
1 | eventTime | eventTime | eventTime | eventTime | eventTime 
2 | eventTimeZoneOffset ||
3 | ErrorDeclaration – declarationTime
4 | ErrorDeclaration <td colspan=5> Test 
  
  
<table>
    <thead>
        <tr>
            <th>Seq.</th>
            <th>ObjectEvent</th>
            <th>AggregationEvent</th>
            <th>TransactionEvent</th>
            <th>TransformationEvent</th>
            <th>AssociationEvent</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td colspan=4>eventTime</td>
        </tr>
        <tr>
            <td>2</td>
            <td>eventTimeZoneOffset</td>
        </tr>
        <tr>
            <td>3</td>
            <td colspan=5>ErrorDeclaration – declarationTime</td>
        </tr>
        <tr>
            <td>3</td>
            <td colspan=5>ErrorDeclaration – correctiveEventIDs (i.e. each individual event ID in exactly the same sequence as it appears in the correctiveEventIDs element)</td>
        </tr>
    </tbody>
</table>


* eventTime
* eventTimeZoneOffset
* ErrorDeclaration – declarationTime
* ErrorDeclaration – reason
* ErrorDeclaration – correctiveEventIDs (i.e. each individual event ID in exactly the same sequence as it appears in the correctiveEventIDs element)
* epcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the epcList)
* parentID  
* inputEpcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the inputEpcList)
* outputEpcList – epc (i.e. each individual EPC in exactly the same sequence as it appears in the outputEpcList)
* quantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the quantityList)
* inputQuantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the inputQuantityList)
* outputQuantityList – epcClass (i.e. each individual epcClass in exactly the same sequence as it appears in the outputQuantityList)
* action
* bizStep
* disposition
* readPoint
* bizLocation
* bizTransactionList – bizTransaction (i.e. each individual bizTransaction ID in exactly the same sequence as it appears in the bizTransactionList)
* sourceList – source (i.e. each individual source ID in exactly the same sequence as it appears in the sourceList)
* destinationList – destination (i.e. each individual destination ID in exactly the same sequence as it appears in the destinationList)
* sensorElement – sensorMetaData – time
* sensorElement – sensorMetaData – startTime
* sensorElement – sensorMetaData – endTime
* sensorElement – sensorMetaData – deviceID
* sensorElement – sensorMetaData – deviceMetaData
* sensorElement – sensorMetaData – rawData
* sensorElement – sensorMetaData – dataProcessingMethod
* sensorElement – sensorMetaData – bizRules
* sensorElement – sensorReport – type
* sensorElement – sensorReport – deviceID
* sensorElement – sensorReport – deviceMetaData
* sensorElement – sensorReport – rawData
* sensorElement – sensorReport – dataProcessingMethod
* sensorElement – sensorReport – time
* sensorElement – sensorReport – microorganism
* sensorElement – sensorReport – chemicalSubstance
* sensorElement – sensorReport – value
* sensorElement – sensorReport – stringValue
* sensorElement – sensorReport – booleanValue
* sensorElement – sensorReport – hexBinaryValue
* sensorElement – sensorReport – uriValue
* sensorElement – sensorReport – minValue
* sensorElement – sensorReport – maxValue
* sensorElement – sensorReport – averageValue
* sensorElement – sensorReport – sDev
* sensorElement – sensorReport – percRank
* sensorElement – sensorReport – percValue
* sensorElement – sensorReport – uom

## Installation
tbd

## Usage/Short test script 
tbd

## References
* EPCIS Standard, v. 1.2: https://www.gs1.org/standards/epcis
* Core Business Vocabulary (CBV) Standard, v. 1.2.2: https://www.gs1.org/standards/epcis
