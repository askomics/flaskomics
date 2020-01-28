During integration of TSV/CSV, GFF and BED files, AskOmics create RDF triples that describe the data. This set of triple are called *Abstraction*. *Abstraction* is a set of RDF triples who describes the data. This triples define *Entities*, *Attributes* and *Relations*. Abstraction is used to build the *Query builder*.

Raw RDF can be integrated into AskOmics. In this case, abstraction have to be built manually. The following documentation explain how to write an AskOmics abstraction in turtle format.

# Prefixes

AskOmics use the following prefixes.

```turtle
PREFIX : <http://www.semanticweb.org/user/ontologies/2018/1#>
PREFIX askomics: <http://www.semanticweb.org/askomics/ontologies/2018/1#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX faldo: <http://biohackathon.org/resource/faldo/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```
<br />

!!! info
    Prefixes `:` and `askomics:` are defined in the AskOmics config file (`config/askomics.ini`)

# Entity

The entity is a class. In the query builder, it is represented with a graph node.

```turtle
:EntityName rdf:type :entity .
:EntityName rdf:type owl:Class .
:EntityName rdf:type :startPoint .
:EntityName rdfs:label "EntityName" .
```
<br />

!!! info
    `:EntityName rdf:type :startPoint` is not mandatory. If the entity have this triple, a query can be started with this this node.

# Attributes

Attributes are linked to an entity. 3 types of attributes are used in AskOmics: *numeric*, *text* and  *category*.

## Numeric

```turtle
:numeric_attribute rdf:type owl:DatatypeProperty .
:numeric_attribute rdfs:label "numeric_attribute" .
:numeric_attribute rdfs:domain :EntityName .
:numeric_attribute rdfs:range xsd:decimal .
```

## Text

```turtle
:text_attribute rdf:type owl:DatatypeProperty .
:text_attribute rdfs:label "text_attribute" .
:text_attribute rdfs:domain :EntityName .
:text_attribute rdfs:range xsd:string .
```

## Category

Category is an attribute that have a limited number of values. All values of the category are stored in the abstraction. The ttl below represent a category `category_attribute` who can takes 2 values: `value_1` and `value_2`.

```turtle
:category_attribute rdf:type owl:ObjectProperty .
:category_attribute rdf:type :AskomicsCategory .
:category_attribute rdfs:label "category_attribute" .
:category_attribute rdfs:domain :EntityName .
:category_attribute rdfs:range :category_attributeCategory .

:category_attributeCategory askomics:category :value_1 .
:category_attributeCategory askomics:category :value_2 .

:value_1 rdf:type :category_attributeCategoryValue .
:value_1 rdfs:label "value_1" .

:value_2 rdf:type :category_attributeCategoryValue .
:value_2 rdfs:label "value_2" .
```

## Faldo

[FALDO](https://bioportal.bioontology.org/ontologies/FALDO) is a simple ontology to describe sequence feature positions and regions. AskOmics can use FALDO to describe this kind of entities. GFF, BED and some CSV/TSV are converted with FALDO.

A FALDO entity have to be declared as FALDO on the abstraction. If attribute are decribed as FALDO in the abstractio, The data triples have to use FALDO to describe the data.

```turtle
:FaldoEntity rdf:type :entity .
:FaldoEntity rdf:type :faldo .
:FaldoEntity rdf:type owl:Class .
:FaldoEntity rdf:type :startPoint .
:FaldoEntity rdfs:label "FaldoEntity" .
```

Four FALDO attributes are supported by AskOmics: reference, strand, start and end.

### faldo:reference

A faldo:reference attribute derive from a Category attribute.

```turtle
:reference_attribute rdf:type askomics:faldoReference .
:reference_attribute rdf:type :AskomicsCategory .
:reference_attribute rdf:type owl:ObjectProperty .
:reference_attribute rdfs:label "reference_attribute" .
:reference_attribute rdfs:domain :EntityName .
:reference_attribute rdfs:range :reference_attributeCategory.
```

### faldo:strand

faldo:strand is also a category.

```turtle
:strand_attribute rdf:type askomics:faldoStrand .
:strand_attribute rdf:type :AskomicsCategory .
:strand_attribute rdf:type owl:ObjectProperty .
:strand_attribute rdfs:label "strand_attribute" .
:strand_attribute rdfs:domain :EntityName .
:strand_attribute rdfs:range :strand_attributeCategory.
```

### faldo:start and faldo:end

faldo:start and faldo:end are numeric attributes.

```turtle
:start_attribute rdf:type askomics:faldoStart .
:start_attribute rdf:type owl:DatatypeProperty .
:start_attribute rdfs:label "start_attribute" .
:start_attribute rdfs:domain :EntityName .
:start_attribute rdfs:range xsd:decimal .
```

```turtle
:end_attribute rdf:type askomics:faldoEnd .
:end_attribute rdf:type owl:DatatypeProperty .
:end_attribute rdfs:label "end_attribute" .
:end_attribute rdfs:domain :EntityName .
:end_attribute rdfs:range xsd:decimal .
```

# Relations

Entities are linked between them with relations. Relations are displayed with arrows between nodes on the query builder. The following turtle explain how relations are described.

```turtle
:relation_example a :AskomicsRelation .
:relation_example a owl:ObjectProperty .
:relation_example rdfs:label "relation_example" .
:relation_example rdfs:domain :EntityName .
:relation_example rdfs:range :EntityName_2 .
```
