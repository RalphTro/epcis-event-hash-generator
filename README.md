# EPCIS Event Hash Generator
This is a proposal/reference implementation for a method to uniquely identify an EPCIS event or validate the integrity thereof. To this end, a syntax-/representation-agnostic approach based on hashing is developed.
The <b>PROTOTYPAL DEMO SOFTWARE</b> takes an EPCIS Document (either formatted in XML or JSON-LD) and returns the hash value(s) of the contained EPCIS events representing a unique fingerprint of the latter. 

![EPCIS event hash generator algorithm illustration](docs/epcisEventHashGenerator.jpg)


## Usage (for the inconvenient)
The script may be used as a command line utility like this:
```
python src/EpcisEventHashGenerator.py test/sensorObjectEvent.xml
```

See
```
python src/EpcisEventHashGenerator.py -h
```
for usage information.

Tests are run via
```
cd src; pytest
```

## Introduction  
There are situations in which organisations require to uniquely refer to a specific EPCIS event. For instance, companies may only want to store the <b>hash value of a given EPCIS event on a distributed shared ledger ('blockchain')</b> instead of any actual payload. Digitally signed and in conjunction with a unique timestamp, this is a powerful and effective way to prove the integrity of the underlying event data. Another use case consists to use such an approach to <b>populate the eventID field with values that are intrinsic to the EPCIS event</b> - if an organisation captures an event without an eventID (which is not required as of the standard) and sends that event to a business partner who needs to assign a unique ID, they can agree that the business partner populates the eventID field applying this methodology before storing the event on the server. If the organisation later wants to query for that specific event, it knows how the eventID was created, thus is able to query for it through the eventID value.
EPCIS events have a couple of differences to other electronic documents:
+ They are embedded in an EPCIS document that can contain multiple events 
+ As of EPCIS 2.0, it is permitted to capture and share EPCIS data through two different syntaxes (XML and JSON/JSON-LD)
+ EPCIS events provides ample flexibility to include user-specific extensions 
+ When expressed in JSON/JSON-LD, the sequence of elements may vary

This is why industry needs to have a consistent, reliable approach to create a hash value that is viable to uniquely identify a specific EPCIS event. 


## Requirements

For any algorithm that is to be considered a faithful hash of an EPCIS event, we require the following properties:

+ Different (valid) serialisations of the **same event** need to yield the **same hash**.
+ In particular, if serialised in XML, the hash must be independend of irrelevant whitespace, ordering of elements in an unordered list, the name used for namespaces, etc. (see e.g. https://en.wikipedia.org/wiki/XML_Signature#XML_canonicalization for more details on the matter).
+ The same event serialised in JSON/JSON-LD or XML must yield the same hash.
+ Any relevant **change of an event** must lead to a **change of the hash**. In particular, the hash must change if
  - any value of any field present in the event is changed.
  - a field is added or removed.


## Algorithm

For hashing strings, standard implementations of the relevant hash algorithms (such as sha-256) are avaiable for all relevant languages. Hence, the focus here is on deriving a so-called *pre-hash string* representation of an EPCIS event which fulfils the above requirements and can subsequently be passed to a standard hashing algorithm.

To calculate the pre-hash string, extract and concatenate EPCIS event key-value pairs exactly according to the following sequence. First, ALL attribute names/values of ALL EPCIS standard fields (*except recordTime*), are concatenated as one string. Thereby, each value is assigned to its key through an equal sign ('='). Then, this string is appended by ALL user extensions comprising their key names (namespace followed by a pound sign ('#') and the respective local name), and, if present, the actual value, prefixed by an equal sign ('=').  

Note that all key/value pairs MUST be added in the identical order as specified below (corresponding to the order in which they are specified in the EPCIS standard). Data MUST NOT be added if any field is omitted in a given event or does not apply. Whitespace at the beginning and end of string values is to be cropped (by the definition of XML).
  
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
            <td colspan=5>eventType</td>
        </tr>
        <tr>
            <td>2</td>
            <td colspan=5>eventTime</td>
        </tr>
        <tr>
            <td>3</td>
            <td colspan=5>eventTimeZoneOffset</td>
        </tr>
        <tr>
            <td>4</td>
            <td colspan=5>eventID</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>Note: Even if an event ID value is already present (which is NOT required!), this method may still be beneficial, e.g. when organisations require to store a unique fingerprint of EPCIS events on a distributed shared ledger.<i/></td>
        </tr>
        <tr>
            <td>5</td>
            <td colspan=5>ErrorDeclaration – declarationTime</td>
        </tr>
        <tr>
            <td>6</td>
            <td colspan=5>ErrorDeclaration – reason</td>
        </tr>
        <tr>
            <td>7</td>
            <td colspan=5>ErrorDeclaration – correctiveEventIDs</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All individual event IDs being part of the correctiveEventIDs element MUST be sequenced in lexicographical order</i></td>
        </tr>
       <tr>
          <td>8</td>
          <td colspan=2>-</td>
          <td>bizTransactionList – bizTransaction</td>
          <td colspan=2>-</td>
      </tr>
      <tr>
        <td/>
        <td colspan=5><i>All individual bizTransaction IDs being part of the bizTransactionList MUST be sequenced in lexicographical order  </i></td>
      </tr>
      <tr>
            <td>9</td>
            <td>epcList – epc</td>
            <td>parentID</td>
            <td>parentID</td>
            <td>inputEPCList – epc</td>
            <td>parentID</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All EPC values being part of the respective lists MUST be sequenced in lexicographical order</i>             </td>
        </tr>
        <tr>
            <td>10</td>
            <td>quantityList - quantityElement (epcClass + quantity + uom)</td>
            <td>childEPCs – epc</td>
            <td>epcList – epc</td>
            <td>inputQuantityList – quantityElement (epcClass + quantity + uom)</td></td>
            <td>childEPCs – epc</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All Quantity Elements being part of the respective lists MUST be sequenced in lexicographical order</i>             </td>
        </tr>
        <tr>
            <td>11</td>
            <td/>
            <td>childQuantityList – quantityElement (epcClass + quantity + uom)</td>
            <td>quantityList – quantityElement (epcClass + quantity + uom)</td>
            <td>outputEPCList – epc</td></td>
            <td>childQuantityList – quantityElement (epcClass + quantity + uom)</td>
        </tr>
        <tr>
            <td>12</td>
            <td/>
            <td colspan=2>-</td>
            <td>outputQuantityList – quantityElement (epcClass + quantity + uom)</td></td>
            <td colspan=1>-</td>
        </tr>
        <tr>
            <td>13</td>
            <td>action</td>
            <td>action</td>
            <td>action</td>
            <td>transformationID</td>
            <td>action</td>
        </tr>
        <tr>
            <td>14</td>
            <td colspan=5>bizStep</td>
        </tr>
        <tr>
            <td>15</td>
            <td colspan=5>disposition</td>
        </tr>
        <tr>
            <td>16</td>
            <td colspan=5>readPoint</td>
        </tr>
        <tr>
            <td>17</td>
            <td colspan=5>bizLocation</td>
        </tr>
        <tr>
            <td>18</td>
            <td colspan=2>bizTransactionList – bizTransaction</td>
            <td>-</td>
            <td colspan=2>bizTransactionList – bizTransaction</td>
        </tr>
        <tr>
            <td>19</td>
            <td colspan=5>sourceList – source</td>
        </tr>
        <tr>
            <td>20</td>
            <td colspan=5>destinationList – destination</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All individual source/destination IDs being part of the respective lists MUST be sequenced in lexicographical order</td>
        </tr>
        <tr>
            <td>21</td>
            <td colspan=5>sensorElement – sensorMetaData (time + startTime + endTime + deviceID + deviceMetaData + rawData + dataProcessingMethod + bizRules)</td>
        </tr>
        <tr>
            <td>22</td>
            <td colspan=5>sensorElement – sensorReport (type + deviceID + deviceMetaData + rawData + dataProcessingMethod + time + microorganism + chemicalSubstance + value + stringValue + booleanValue + hexBinaryValue + uriValue + minValue + maxValue + meanValue + sDev + percRank + percValue + uom)</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All Sensor Elements MUST be sequenced in lexicographical order</i>             </td>
        </tr>
        <tr>
            <td>23</td>
            <td>ILMD</td>
            <td colspan=2>-</td>
            <td>ILMD</td>
            <td>-</td>
        </tr>      
        <tr>
            <td/>
            <td colspan=5><i>All ILMD field values, irrespective of their level and field name, MUST be sequenced in lexicographical order</td>
        </tr>
        <tr>
            <td>24</td>
            <td colspan=5>User extensions</td>
        </tr>
        <tr>
            <td/>
            <td colspan=5><i>All user extension element names irrespective of their level MUST be prefixed with their namespace, followed by a pound sign ('#'). If they contain a value, the value MUST be prefixed with an equal sign ('='). <br>
              (Example: https://ns.example.com/epcis#myField=abc123) <br>
              Then, all fields belonging to the same level MUST be sequenced in lexicographical order depending on the contained values.
        </tr>
    </tbody>
</table>

The last step consists in **embedding the resulting hash value in the 'ni' URI scheme as specified in RFC6920**, as follows:<br>
ni:///{digest algorithm};{digest value} <br>
(i.e. characters 'n', 'i', followed by one colon (':'), three slash characters ('/'), the digest algorithm, one semicolon (';'), and the digest value)<br>
For instance, when applying sha-256 and sha-512 for the pre-hash string, the corresponding ni Hash URIs would look as follows:<br>
ni:///sha-256;ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae <br>
ni:///sha-512;daef4953b9783365cad6615223720506cc46c5167cd16ab500fa597aa08ff964<br>eb24fb19687f34d7665f778fcb6c5358fc0a5b81e1662cf90f73a2671c53f991


For better understanding, the following illustration includes the data content of a simple EPCIS event (including a couple of user extensions - all defined under 'https://ns.example.com/epcis'), shows the corresponding pre-hash string as well as the canonical hash value of that event.

![Example EPCIS event pre-hash computation](docs/hashingAlgorithmLogicIllustration.jpg)

## References
* EPCIS Standard, v. 1.2: https://www.gs1.org/standards/epcis
* Core Business Vocabulary (CBV) Standard, v. 1.2.2: https://www.gs1.org/standards/epcis
* RFC 6920, Naming Things with Hashes, https://tools.ietf.org/html/rfc6920
* Named Information Hash ALgorithm Registry, https://www.iana.org/assignments/named-information/named-information.xhtml


## License

<img alt="MIT" style="border-width:0" src="https://opensource.org/files/OSIApproved_1.png" width="150px;"/><br />

Copyright 2020 | Ralph Tröger <ralph.troeger@gs1.de> and Sebastian Schmittner <schmittner@eecc.info>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
