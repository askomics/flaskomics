During integration of TSV/CSV, GFF and BED files, AskOmics create RDF triples that describe the data. This set of triple are called *Abstraction*. These triples define *Entities*, *Attributes* and *Relations*. The abstraction is used to build the *Query builder*.

Raw RDF can be integrated into AskOmics. In this case, the abstraction have to be built manually. The following documentation explain how to write manually write an AskOmics abstraction in turtle format.

!!! warning
    Starting from 4.4, attributes & relations are defined using blank nodes, to avoid overriding information.
    They are linked to the correct node using askomics:uri

# Namespaces

AskOmics use the following namespaces.

```turtle
PREFIX : <http://askomics.org/data/>
PREFIX askomics: <http://askomics.org/internal/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX faldo: <http://biohackathon.org/resource/faldo/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
```
<br />

!!! note "Info"
    Namespaces `:` and `askomics:` are defined in the AskOmics config file (`config/askomics.ini`)

# Entity

The entity is a class. In the query builder, it is represented with a graph node.

```turtle
:EntityName rdf:type askomics:entity .
:EntityName rdf:type owl:Class .
:EntityName rdf:type askomics:startPoint .
:EntityName rdfs:label "EntityName" .
# Optional (use if no label)
:EntityName askomics:instancesHaveNoLabels true .
# Optional (use if you wish to use a specific attribute as label)
:EntityName askomics:instancesLabel :attributeUri .
```
<br />

!!! note "Info"
    `:EntityName rdf:type :startPoint` is not mandatory. If the entity have this triple, a query can be started with this this node.

!!! note "Info"
    `:EntityName rdfs:label "EntityName"` is optional. If your entity has no label, you can use `:EntityName askomics:instancesHaveNoLabels true` instead. In the query view, the label tab will not be displayed. The URI attribute will be set visible by default

!!! note "Info"
    If you set 'askomics:instancesLabel' to an attribute URI, this attribute will be set to 'visible' by default. The 'label' attribute will not be displayed.

# Attributes

Attributes are linked to an entity. 3 types of attributes are used in AskOmics: *numeric*, *text* and  *category*.

## Numeric

```turtle
_:blank rdf:type owl:DatatypeProperty .
_:blank rdfs:label "numeric_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range xsd:decimal .
_:blank askomics:uri :numeric_attribute_uri .
```

## Text

```turtle
_:blank rdf:type owl:DatatypeProperty .
_:blank rdfs:label "text_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range xsd:string .
_:blank askomics:uri :text_attribute_uri .
```

## Category

Category is an attribute that have a limited number of values. All values of the category are stored in the abstraction. The ttl below represent a category `category_attribute` who can takes 2 values: `value_1` and `value_2`.

```turtle
_:blank rdf:type owl:ObjectProperty .
_:blank rdf:type askomics:AskomicsCategory .
_:blank rdfs:label "category_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range :category_attributeCategory .
_:blank askomics:uri :category_attribute_uri .

:category_attributeCategory askomics:category :value_1 .
:category_attributeCategory askomics:category :value_2 .

:value_1 rdf:type :category_attributeCategoryValue .
:value_1 rdfs:label "value_1" .

:value_2 rdf:type :category_attributeCategoryValue .
:value_2 rdfs:label "value_2" .
```

## Faldo

[FALDO](https://bioportal.bioontology.org/ontologies/FALDO) is a simple ontology to describe sequence feature positions and regions. AskOmics can use FALDO to describe this kind of entities. GFF, BED and some CSV/TSV are converted with FALDO.

A FALDO entity have to be declared as FALDO on the abstraction. If attribute are described as FALDO in the abstraction, the data triples have to use FALDO to describe the data.

```turtle
:FaldoEntity rdf:type askomics:entity .
:FaldoEntity rdf:type askomics:faldo .
:FaldoEntity rdf:type owl:Class .
:FaldoEntity rdf:type askomics:startPoint .
:FaldoEntity rdfs:label "FaldoEntity" .
```

Four FALDO attributes are supported by AskOmics: reference, strand, start and end.

### Faldo ontology

AskOmics expect faldo entities to follow the faldo ontology for triple definition. Ex:

```turtle
# Reference
:Entity faldo:location/faldo:begin/faldo:reference "value"
# strand
:Entity faldo:location/faldo:begin/rdf:type "value"
# Start
:Entity faldo:location/faldo:begin/faldo:position "value"
# Stop.
:Entity faldo:location/faldo:end/faldo:position "value"
```

### faldo:reference

A faldo:reference attribute derive from a Category attribute.

```turtle
_:blank rdf:type askomics:faldoReference .
_:blank rdf:type askomics:AskomicsCategory .
_:blank rdf:type owl:ObjectProperty .
_:blank rdfs:label "reference_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range :reference_attributeCategory.
_:blank askomics:uri :reference_attribute


:reference_attributeCategory askomics:category :value_1 .
:reference_attributeCategory askomics:category :value_2 .

:value_1 rdf:type :reference_attributeCategoryValue .
:value_1 rdfs:label "value_1" .

:value_2 rdf:type :reference_attributeCategoryValue .
:value_2 rdfs:label "value_2" .

```

### faldo:strand

faldo:strand is also a category.

```turtle
_:blank rdf:type askomics:faldoStrand .
_:blank rdf:type askomics:AskomicsCategory .
_:blank rdf:type owl:ObjectProperty .
_:blank rdfs:label "strand_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range :strand_attributeCategory .
_:blank askomics:uri :strand_attribute

:strand_attributeCategory askomics:category faldo:ForwardStrandPosition .
:strand_attributeCategory askomics:category faldo:ReverseStrandPosition .

faldo:ForwardStrandPosition rdf:type :strand_attributeCategoryValue .
faldo:ForwardStrandPosition rdfs:label "+" .

faldo:ReverseStrandPosition rdf:type :strand_attributeCategoryValue .
faldo:ReverseStrandPosition rdfs:label "-" .
```

!!! note "Info"
    For homogeneity with GFF and BED integration, it's better to use '+', '-' or '.' as the strand label.

### faldo:start and faldo:end

faldo:start and faldo:end are numeric attributes.

```turtle
_:blank rdf:type askomics:faldoStart .
_:blank rdf:type owl:DatatypeProperty .
_:blank rdfs:label "start_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range xsd:decimal .
_:blank askomics_uri :start_attribute
```

```turtle
_:blank rdf:type askomics:faldoEnd .
_:blank rdf:type owl:DatatypeProperty .
_:blank rdfs:label "end_attribute" .
_:blank rdfs:domain :EntityName .
_:blank rdfs:range xsd:decimal .
_:blank askomics:uri :end_attribute
```

### *Shortcut* faldo triples

The default faldo ontology uses a chain of triple to describe the position (ex, faldo:location/faldo:begin/faldo:position).
This make *faldo queries* (included_in/overlap_with/distant_from) extremely slow. To improve query time, AskOmics can use 'shortcut triples', direct relations between the Entity and the reference/strand, to quickly filter entities on the same reference/strand/both. For example:

```turtle
:EntityName askomics:faldoReference reference_uri .
:EntityName askomics:faldoBegin begin_value .
:EntityName askomics:faldoEnd end_value .
:EntityName askomics:faldoStrand strand_uri .
:EntityName askomics:referenceStrand reference_strand_uri .
```

To improve query times further, AskOmics will break down the entity genomic position in blocks (block size if defined in the configuration file).
This improve query time by filtering all entities having 'common blocks'. Each entity will span at least two blocks. Additional blocks will be created to include the reference and the strand.
For instance:

```turtle
:EntityName askomics:includeIn block1_uri .
:EntityName askomics:includeIn block2_uri .
:EntityName askomics:includeInReference block1_reference_uri .
:EntityName askomics:includeInReference block2_reference_uri .
:EntityName askomics:includeInReferenceStrand block1_reference_strand_uri .
:EntityName askomics:includeInReferenceStrand block2_reference_strand_uri .
:EntityName askomics:includeInStrand block1_strand_uri .
:EntityName askomics:includeInStrand block1_strand_uri .
```

!!! note "Info"
    When using 'BothStrand', make sur to add 'ForwardStrandPosition' and 'ReverseStrandPosition' to these additional triples, or they won't be matched on the 'same strand' query.

# Relations

Entities are linked between them with relations. Relations are displayed with arrows between nodes on the query builder. The following turtle explain how relations are described. To avoid overwriting information, relations are described using a blank node. The relation `:RelationExample`, linking `EntitySource` to `EntityTarget`, with the label *relation_example*, will be defined as follows:  

```turtle
_:blank askomics:uri :RelationExample .
_:blank a askomics:AskomicsRelation .
_:blank a owl:ObjectProperty .
_:blank rdfs:label "relation_example" .
_:blank rdfs:domain :EntitySource .
_:blank rdfs:range :EntityTarget .
# Optional information for future-proofing
_:blank dcat:endpointURL <url...> .
_:blank dcat:dataset <file_turtle_XXXXX_gene_tsv> .
```

!!! note "Info"
    If defining an 'indirect relation', you can add a `_:blank askomics:isIndirectRelation true` triple.


# Federation

To describe a remote dataset, you can either fill out the "Distant endpoint" and optionally the "Distant graph" fields when integrating an RDF dataset, or you could add description triples in your dataset, as follows:

```turtle
_:blank prov:atLocation "https://my_remote_endpoint/sparql" .
_:blank dcat:Dataset <my_remote_graph> .
```

# Ontologies

Ontologies needs to be are defined as follows:

```turtle
<ontology_uri> rdf:type askomics:ontology .
<ontology_uri> rdf:type owl:Ontology .
:EntityName rdfs:label "OntologyLabel" .
```

!!! note "Info"
    Make sure to use `rdfs:label`, even if your classes use another type of label.

You will then need to add any relations and attributes using blank nodes:

```turtle
# SubCLassOf relation
_:blank1 a askomics:AskomicsRelation .
_:blank1	askomics:uri rdfs:subClassOf .
_:blank1 rdfs:label "subClassOf" .
_:blank1	rdfs:domain <ontology_uri> .
_:blank1	rdfs:range <ontology_uri> .
# Optional
_:blank1	askomics:isRecursive true .

# Ontology attribute 'taxon rank'
_:blank2 a owl:DatatypeProperty .
_:blank2 askomics:uri <http://purl.bioontology.org/ontology/NCBITAXON/RANK> .
_:blank2 rdfs:label "Taxon rank" .
_:blank2 rdfs:domain <ontology_uri> .
_:blank2 rdfs:range xsd:string .
```

!!! note "Info"
    `askomics:isRecursive` will let users send a 'recursive' (via property path) query using this relation. (Ex: all descendants of a class, using the 'subClassOf' relation)

With these triples, your ontology will appears in the graph view.
You can then either add your classes directly, or refer to an external endpoint / graph

## Adding the classes directly

Here is an example of an ontological class:

```turtle
<class_uri> rdf:type owl:Class .
<class_uri> rdfs:subClassOf <another_class_uri> .
<class_uri> <rank_uri> "order" .
<class_uri> skos:prefLabel "OntologyLabel" .
```

!!! warning
    For now, AskOmics expect the classes to be defined by 'owl:Class'

!!! note "Info"
    The label does not need to be `rdfs:label`, but you will need to specify the correct label in the UI.

## Using federated queries

If instead you have access to a remote SPARQL endpoint, you can indicate it here:

```turtle
_:blank prov:atLocation "https://my_remote_endpoint/sparql" .
# Optional: Set a specific graph for remote queries
_:blank dcat:Dataset <my_remote_graph> .
```
