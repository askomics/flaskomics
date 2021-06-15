# CSV/TSV files

AskOmics will integrate a CSV/TSV file using its header. The *type* of each column will be predicted, but you will be able to modify it before integration.


## Entity (first column)

### Entity URI

The first column of the file will manage the entity itself : the column name will become the entity name, and the values will become the entity **URI**.  
The **uri** will be created as follows :

* If the value is an **url**, it will be integrated as it is.
* If the value is a **CURIE**, it will be transformed in a full uri before integration. The list of managed CURIE format is available [here](https://github.com/askomics/flaskomics/blob/master/askomics/libaskomics/prefix.cc.json)
* Else, the value will be added to either the *askomics base data uri* or a custom base uri if specified in the integration form.

!!! Warning
    Unless you are trying to merge entities, make sure your uris are unique across **both your personal and public datasets**.


### Entity type

The entity type can either be "starting entity", or "entity". If "starting entity", it may be used to start a query on the AskOmics homepage.

### Inheritance

The entity can inherit the attributes and relations of a 'mother' entity. Meaning, you will be able to query the sub-entity on both its own, and its 'mother' attributes and relations. The 'mother' entity however will not have access to any 'daughter' attributes or relations.

To setup inheritance, the column name will need to be of the form *daughter_entity_name*<*mother_entity_name*. Make sure the uris match between "mother" entities and "daughter" entities.

## Attributes

Each column after the first one will be integrated as an *attribute* of the entity. The column name will be set as the name of the attribute. Several attribute types are available (AskOmics will try to guess the type of a column based on whether the column name contains a specific term). The type of an attribute will dictate the way it will be managed in the query form (eg: text field, value selector, etc...)

Attributes can take the following types:

### Base types

- Numeric: if all the values are numeric
- Text: if all the values are strings
- Date: if all the values are dates (managed using dateutil.parser) (Autodetected terms : 'date', 'time', 'birthday', 'day')
- Category: if there is a limited number of repeated values

### FALDO types

If the entity describe a locatable element on a genome (based on the FALDO ontology):

- [Reference](http://biohackathon.org/resource/faldo#reference): chromosome (Autodetected terms : 'chr', 'ref')
- [Strand](http://biohackathon.org/resource/faldo#StrandedPosition): strand (Autodetected terms : 'strand')
- Start: start position (Autodetected terms : 'start', 'begin')
- End: end position (Autodetected terms : 'end', 'stop')

### Relation types

A column can also symbolise a relation to another entity. In this case, the column name must be of the form *relationName@RelatedEntityName*. Two types are available :

- Directed: Relation from this entity to the targeted one (e.g. A is B’s father, but B is not A’s father)
- Symetric: Relation that works in both directions (e.g. A loves B, and B loves A)

!!! Warning
    The content of the column must the the URIs of the related entity. (The related entity does not need to exist at this point, it can be created later)

Linked URIs must match one of these three formats :

- Full URI
- CURIE
- Simple value (the value will transformed into an URI with the *askomics base data uri*)

This link between entities will show up in the query screen, allowing users to query related entities.

!!! info
    Entities using FALDO attributes will be automatically linked, without needing an explicit link.


!!! Warning
    For federated queries, the syntax is slighly different. Please refer to [this page](abstraction.md#linking-your-own-data) for more information.


# GFF files

!!! Warning
    Only the GFF3 format is managed by AskOmics.

You will be able to select the entities you wish to integrate beforehand. Available entities are the values of the 'type' column of the GFF file. The relations betwen entities will also be integrated.

Extracted attributes are the following :

- Reference
- Strand
- Start
- End
- Any attribute in the "attributes" column ("Parents" and "Derives_from" will be converted in relations)

# BED files

BED files will be transformed in entities (the default entity name will be the file name, but it can be customized).

Extracted attributes are the following :

- Reference
- Strand
- Start
- End
- Score
